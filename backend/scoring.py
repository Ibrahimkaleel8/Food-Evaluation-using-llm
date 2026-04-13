from .datatypes import NutritionResponse, UserProfile, HealthCondition

def score_label(score: float) -> str:
    if score >= 80:
        return "excellent"
    elif score >= 60:
        return "good"
    elif score >= 40:
        return "moderate"
    else:
        return "poor"

def compute_health_score(nutrition: NutritionResponse, profile: UserProfile) -> float:
    # Base score starts at nutrition.health_score from the LLM
    score = nutrition.health_score
    
    # All profiles: reward fiber_g > 5g (+10), penalize fiber_g < 1g (-5)
    if nutrition.fiber_g > 5.0:
        score += 10
    elif nutrition.fiber_g < 1.0:
        score -= 5
        
    # Apply rules based on health conditions
    for condition in profile.conditions:
        if condition == HealthCondition.DIABETES:
            if nutrition.carbs_g > 30.0:
                score -= 20
        elif condition == HealthCondition.HIGH_CHOLESTEROL:
            if nutrition.fat_g > 20.0:
                score -= 15
        elif condition == HealthCondition.HYPERTENSION:
            # We don't have sodium tracked definitively in the schema, 
            # but if it was, we would penalize it. We can add a placeholder 
            # or rely on the LLM's base score which should catch sodium.
            # But we can reward potassium if key_vitamins/minerals lists it.
            if any("potassium" in v.lower() for v in nutrition.key_vitamins):
                score += 5
        elif condition == HealthCondition.OBESITY:
            if nutrition.calories > 300.0:
                score -= 10
                
    # Also check goal
    if profile.goal == "weight_loss":
        if nutrition.calories > 300.0:
            score -= 10

    # Clamp result to 0–100
    score = max(0.0, min(100.0, float(score)))
    return score
