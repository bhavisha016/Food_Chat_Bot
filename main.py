# Author: Dhaval Patel (modified for Dialogflow Messenger)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import db_helper
import generic_helper

app = FastAPI()

# store orders per session
inprogress_orders = {}


# 🔹 SINGLE, SAFE RESPONSE FORMAT FOR DIALOGFLOW MESSENGER
def df_response(text: str):
    return JSONResponse(content={
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [text]
                }
            }
        ]
    })


@app.post("/")
async def handle_request(request: Request):
    payload = await request.json()

    intent = payload["queryResult"]["intent"]["displayName"]
    parameters = payload["queryResult"].get("parameters", {})
    output_contexts = payload["queryResult"].get("outputContexts", [])

    session_id = generic_helper.extract_session_id(output_contexts[0]["name"])

    intent_handler_dict = {
        "order.add - context: ongoing-order": add_to_order,
        "order.remove - context: ongoing-order": remove_from_order,
        "order.complete - context: ongoing-order": complete_order,
        "track.order - context: ongoing-tracking": track_order
    }

    handler = intent_handler_dict.get(intent)
    if handler:
        return handler(parameters, session_id)

    return df_response("Sorry, I didn’t understand that.")


# ---------------- ORDER HELPERS ---------------- #

def save_to_db(order: dict):
    order_id = db_helper.get_next_order_id()

    for food_item, quantity in order.items():
        rcode = db_helper.insert_order_item(food_item, quantity, order_id)
        if rcode == -1:
            return -1

    db_helper.insert_order_tracking(order_id, "in progress")
    return order_id


# ---------------- INTENTS ---------------- #

def add_to_order(parameters: dict, session_id: str):
    food_items = parameters.get("food-item", [])
    quantities = parameters.get("number", [])

    if isinstance(food_items, str):
        food_items = [food_items]
    if isinstance(quantities, (int, float)):
        quantities = [quantities]

    if len(food_items) != len(quantities):
        return df_response(
            "Please specify food items and quantities clearly."
        )

    new_items = dict(zip(food_items, quantities))

    if session_id in inprogress_orders:
        inprogress_orders[session_id].update(new_items)
    else:
        inprogress_orders[session_id] = new_items

    order_str = generic_helper.get_str_from_food_dict(
        inprogress_orders[session_id]
    )

    return df_response(
        f"So far you have: {order_str}. Do you need anything else?"
    )


def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return df_response(
            "I can't find your order. Please start a new order."
        )

    food_items = parameters.get("food-item")

    if isinstance(food_items, list):
        food_item = food_items[0]
    else:
        food_item = food_items

    current_order = inprogress_orders[session_id]

    if food_item in current_order:
        del current_order[food_item]

        if current_order:
            order_str = generic_helper.get_str_from_food_dict(current_order)
            return df_response(
                f"Removed {food_item}. Remaining items: {order_str}"
            )
        else:
            return df_response(
                f"Removed {food_item}. Your order is now empty."
            )

    return df_response(f"{food_item} was not in your order.")


def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return df_response(
            "I can't find your order. Please start a new order."
        )

    order = inprogress_orders[session_id]
    order_id = save_to_db(order)

    if order_id == -1:
        return df_response(
            "Sorry, something went wrong while placing your order."
        )

    total = db_helper.get_total_order_price(order_id)
    del inprogress_orders[session_id]

    return df_response(
        f"Your order is placed! Order ID: {order_id}. "
        f"Total amount: {total}. Please pay at delivery."
    )


def track_order(parameters: dict, session_id: str):
    order_id = parameters.get("number")

    if isinstance(order_id, list):
        order_id = order_id[0]

    if not order_id:
        return df_response("Please provide a valid order ID.")

    status = db_helper.get_order_status(int(order_id))

    if status:
        return df_response(
            f"The status of order {order_id} is {status}."
        )

    return df_response(
        f"No order found with order ID {order_id}."
    )
