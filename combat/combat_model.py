class CombatModel:
    """A service model for performing combat calculations."""
    def calculate_damage(self, attacker, defender, roll_result, modifier=0):
        try:
            strength_val = int(attacker.attributes.get("Strength", 10))
            damage = roll_result + (strength_val // 2 - 5) + modifier
            damage = max(0, damage)
            output = f"{attacker.name} attacks {defender.name}.\nRolled {roll_result} + modifier {modifier}.\n" \
                     f"Total damage dealt: {damage}."
            return output, damage
        except Exception as e:
            return f"Error in calculation: {e}", 0

    def check_hit(self, attacker, defender, roll_result, rule_set):
        try:
            if "Dodge Chance" in rule_set['formulas']:
                formula = rule_set['formulas']['Dodge Chance']
                for attr, val in defender.attributes.items():
                    formula = formula.replace(attr, str(val))
                target_ac = eval(formula)
                if roll_result >= target_ac:
                    return f"Hit! ({roll_result} >= {target_ac})", True
                else:
                    return f"Miss! ({roll_result} < {target_ac})", False
            else:
                return "Hit! (No 'Dodge Chance' formula found, default success)", True
        except Exception as e:
            return f"Error checking hit: {e}", False