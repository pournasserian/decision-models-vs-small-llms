from __future__ import annotations

import json

from ..data import fetch, hf_parquet, parquet_rows, sample
from ..schema import Item, Question

REPO = "clinc/clinc_oos"
DOMAINS_URL = "https://raw.githubusercontent.com/clinc/oos-eval/master/data/domains.json"

# Intent names in the 'plus' label order (151 classes; "oos" is index 42), from the dataset card.
INTENTS = [
    "restaurant_reviews", "nutrition_info", "account_blocked", "oil_change_how", "time", "weather", "redeem_rewards",
    "interest_rate", "gas_type", "accept_reservations", "smart_home", "user_name", "report_lost_card", "repeat",
    "whisper_mode", "what_are_your_hobbies", "order", "jump_start", "schedule_meeting", "meeting_schedule",
    "freeze_account", "what_song", "meaning_of_life", "restaurant_reservation", "traffic", "make_call", "text",
    "bill_balance", "improve_credit_score", "change_language", "no", "measurement_conversion", "timer", "flip_coin",
    "do_you_have_pets", "balance", "tell_joke", "last_maintenance", "exchange_rate", "uber", "car_rental", "credit_limit",
    "oos", "shopping_list", "expiration_date", "routing", "meal_suggestion", "tire_change", "todo_list", "card_declined",
    "rewards_balance", "change_accent", "vaccines", "reminder_update", "food_last", "change_ai_name", "bill_due",
    "who_do_you_work_for", "share_location", "international_visa", "calendar", "translate", "carry_on",
    "book_flight", "insurance_change", "todo_list_update", "timezone", "cancel_reservation", "transactions",
    "credit_score", "report_fraud", "spending_history", "directions", "spelling", "insurance", "what_is_your_name",
    "reminder", "where_are_you_from", "distance", "payday", "flight_status", "find_phone", "greeting",
    "alarm", "order_status", "confirm_reservation", "cook_time", "damaged_card", "reset_settings", "pin_change",
    "replacement_card_duration", "new_card", "roll_dice", "income", "taxes", "date", "who_made_you", "pto_request",
    "tire_pressure", "how_old_are_you", "rollover_401k", "pto_request_status", "how_busy", "application_status",
    "recipe", "calendar_update", "play_music", "yes", "direct_deposit", "credit_limit_change", "gas", "pay_bill",
    "ingredients_list", "lost_luggage", "goodbye", "what_can_i_ask_you", "book_hotel", "are_you_a_bot", "next_song",
    "change_speed", "plug_type", "maybe", "w2", "oil_change_when", "thank_you", "shopping_list_update", "pto_balance",
    "order_checks", "travel_alert", "fun_fact", "sync_device", "schedule_maintenance", "apr", "transfer", "ingredient_substitution",
    "calories", "current_location", "international_fees", "calculator", "definition", "next_holiday", "update_playlist",
    "mpg", "min_payment", "change_user_name", "restaurant_suggestion", "travel_notification", "cancel", "pto_used",
    "travel_suggestion", "change_volume",
]
assert len(INTENTS) == 151 and INTENTS[42] == "oos"

OUT_OF_SCOPE = "out of scope"


def domains() -> dict[str, list[str]]:
    return json.loads(fetch(DOMAINS_URL, "clinc-domains.json").read_text(encoding="utf-8"))


def question() -> Question:
    criteria = {}
    for d, intents in domains().items():
        name = d.replace("_", " ")
        examples = ", ".join(i.replace("_", " ") for i in intents[:5])
        criteria[name] = f"{name} requests, for example {examples}"
    criteria[OUT_OF_SCOPE] = "a request that belongs to none of the domains above"
    return Question(
        type="choice",
        instructions="Which domain does this user request belong to?",
        criteria=criteria,
    )


def load(n: int | None) -> list[Item]:
    rows = parquet_rows(hf_parquet(REPO, "plus", "test"), "clinc-plus-test.parquet")
    intent_to_domain = {i: d.replace("_", " ") for d, intents in domains().items() for i in intents}
    q = question()
    items = []
    for i, r in enumerate(rows):
        intent = INTENTS[r["intent"]]
        gold = OUT_OF_SCOPE if intent == "oos" else intent_to_domain[intent]
        items.append(Item(id=f"clinc-{i}", state=r["text"], questions={"domain": q}, gold={"domain": gold}))
    return sample(items, n, "clinc")
