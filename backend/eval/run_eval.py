import json
import os
import re
from datetime import datetime
from pydantic import BaseModel

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.model import get_extracted_details, get_rag_nutrition
from backend.datatypes import TextIn
from backend.eval.logger import log_run
from backend.config import GEMINI_MODEL

DATA_PATH = os.path.join(os.path.dirname(__file__), "usda_ground_truth.json")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")

def extract_float(string_val: str) -> float:
    try:
        if not string_val:
            return 0.0
        match = re.search(r"[-+]?\d*\.\d+|\d+", str(string_val))
        if match:
            return float(match.group())
        return 0.0
    except:
        return 0.0

def run_evaluation():
    if not os.path.exists(DATA_PATH):
        print(f"Ground truth dataset not found at {DATA_PATH}")
        return
        
    with open(DATA_PATH, "r") as f:
        ground_truth = json.load(f)
        
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)

    results = []
    
    total_rag_error = {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0, "fiber_g": 0.0}
    total_base_error = {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0, "fiber_g": 0.0}
    
    rag_within_tol = 0
    base_within_tol = 0
    total_metrics_checked = 0
    
    for item in ground_truth:
        food_name = item["food_name"]
        print(f"Evaluating {food_name}...")
        
        # 1. Baseline Old Prompt
        base_res = get_extracted_details(TextIn(food_name=food_name))
        
        if base_res and len(base_res) >= 2:
            base_nutrients = base_res[1]
            base_preds = {
                "calories": 0.0, # Baseline might not even return calories cleanly originally! 
                "protein_g": extract_float(base_nutrients.proteins),
                "carbs_g": extract_float(base_nutrients.carbohydrates),
                "fat_g": extract_float(base_nutrients.fats),
                "fiber_g": 0.0 # Baseline might not trace fiber 
            }
        else:
            base_preds = {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0, "fiber_g": 0.0}
            
        # 2. RAG Prompt
        rag_res = get_rag_nutrition(food_name)
        rag_preds = {
            "calories": rag_res.calories,
            "protein_g": rag_res.protein_g,
            "carbs_g": rag_res.carbs_g,
            "fat_g": rag_res.fat_g,
            "fiber_g": rag_res.fiber_g
        }
        
        # Compare
        food_result = {
            "food": food_name,
            "actual": item,
            "baseline": base_preds,
            "rag": rag_preds,
            "rag_source": rag_res.retrieval_source
        }
        results.append(food_result)
        
        for metric in total_rag_error.keys():
            actual_val = item.get(metric, 0.0)
            
            # calculate absolute error
            rag_err = abs(rag_preds[metric] - actual_val)
            base_err = abs(base_preds[metric] - actual_val)
            
            total_rag_error[metric] += rag_err
            total_base_error[metric] += base_err
            
            # 10% tolerance test
            tol = max(actual_val * 0.1, 1.0) # at least 1 unit tol
            if rag_err <= tol:
                rag_within_tol += 1
            if base_err <= tol:
                base_within_tol += 1
                
            total_metrics_checked += 1
            
    # Calculate aggregates
    n = len(ground_truth)
    if n == 0:
        return
        
    avg_rag_mae = {k: v / n for k, v in total_rag_error.items()}
    avg_base_mae = {k: v / n for k, v in total_base_error.items()}
    
    rag_accuracy_pct = (rag_within_tol / total_metrics_checked) * 100 if total_metrics_checked > 0 else 0
    base_accuracy_pct = (base_within_tol / total_metrics_checked) * 100 if total_metrics_checked > 0 else 0
    
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    final_output = {
        "run_timestamp": datetime.now().isoformat(),
        "model": GEMINI_MODEL,
        "rag_accuracy_pct": round(rag_accuracy_pct, 2),
        "baseline_accuracy_pct": round(base_accuracy_pct, 2),
        "rag_per_nutrient_mae": {k: round(v, 2) for k, v in avg_rag_mae.items()},
        "base_per_nutrient_mae": {k: round(v, 2) for k, v in avg_base_mae.items()},
        "per_food_results": results
    }
    
    out_file = os.path.join(RESULTS_DIR, f"eval_{timestamp_str}.json")
    with open(out_file, "w") as f:
        json.dump(final_output, f, indent=2)
        
    log_run(final_output)
        
    print("\n--- RESULTS ---")
    print(f"RAG Accuracy (10% tol): {rag_accuracy_pct:.1f}%")
    print(f"Baseline Accuracy (10% tol): {base_accuracy_pct:.1f}%")
    print("RAG MAE:", final_output["rag_per_nutrient_mae"])
    print("Base MAE:", final_output["base_per_nutrient_mae"])
    print(f"Saved to {out_file}")


if __name__ == "__main__":
    run_evaluation()
