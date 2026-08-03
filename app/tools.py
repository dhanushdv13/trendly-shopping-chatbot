import json
import os
from datetime import datetime
from typing import Optional

# Define the absolute paths to the data files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDERS_FILE = os.path.join(BASE_DIR, "data", "orders.json")
POLICY_FILE = os.path.join(BASE_DIR, "data", "trendly_policy.md")

def get_order(order_id: str) -> Optional[dict]:
    """
    Retrieve order details for a given order ID.
    
    Args:
        order_id: The ID of the order to look up (e.g., 'ORD101').
        
    Returns:
        A dictionary containing the order details if found, otherwise None.
    """
    if not os.path.exists(ORDERS_FILE):
        return None
        
    with open(ORDERS_FILE, "r") as f:
        orders = json.load(f)
        
    for order in orders:
        if order.get("order_id") == order_id:
            return order
    return None

def search_policy(query: str) -> str:
    """
    Search the Trendly store policy for information relevant to the query.
    This function reads the policy document and returns the sections that most likely answer the query.
    
    Args:
        query: The customer's question or topic of interest (e.g., "return policy", "exchange", "refund").
        
    Returns:
        A string containing the relevant policy section(s).
    """
    if not os.path.exists(POLICY_FILE):
        return "Policy document not found."
        
    with open(POLICY_FILE, "r") as f:
        content = f.read()
        
    query_lower = query.lower()
    sections = content.split("## ")
    
    relevant_sections = []
    
    # Very basic keyword search logic
    keywords = {
        "return": ["return", "30 days", "unworn"],
        "exchange": ["exchange", "different size"],
        "refund": ["refund", "money back", "timelines", "processing"],
        "shipping": ["shipping", "delivery", "track"],
        "missing": ["missing", "lost", "damaged", "package"]
    }
    
    # Determine search keys from query
    search_keys = []
    for k, v_list in keywords.items():
        if k in query_lower or any(v in query_lower for v in v_list):
            search_keys.append(k)
            
    if not search_keys:
        # Default to checking if any keyword is in the section title
        search_keys = [query_lower]
        
    for section in sections[1:]: # Skip the first split which is the title
        section_lower = section.lower()
        if any(sk in section_lower for sk in search_keys):
            relevant_sections.append("## " + section.strip())
            
    if not relevant_sections:
        return "I could not find a specific policy section matching your query. Please ask a human agent for more details."
        
    return "\n\n".join(relevant_sections)

def check_return_eligibility(order_id: str) -> dict:
    """
    Check if a given order is eligible for a return based on the store's return policy.
    
    Args:
        order_id: The ID of the order.
        
    Returns:
        A dictionary with 'eligible' (bool) and 'reason' (str) explaining why it is or isn't eligible.
    """
    order = get_order(order_id)
    if not order:
        return {"eligible": False, "reason": "Order not found."}
        
    if order.get("status") != "delivered":
        return {"eligible": False, "reason": f"Order status is '{order.get('status')}'. Items can only be returned after they are delivered."}
        
    if order.get("is_sale_item"):
        return {"eligible": False, "reason": "Items marked as 'Sale' or 'Clearance' are final sale and not eligible for returns."}
        
    delivery_date_str = order.get("delivery_date")
    if not delivery_date_str:
        return {"eligible": False, "reason": "No delivery date recorded for this order."}
        
    try:
        delivery_date = datetime.strptime(delivery_date_str, "%Y-%m-%d").date()
        today = datetime.now().date()
        days_since_delivery = (today - delivery_date).days
        
        if days_since_delivery > 30:
            return {"eligible": False, "reason": f"The return window is 30 days. This item was delivered {days_since_delivery} days ago."}
    except ValueError:
        return {"eligible": False, "reason": "Invalid delivery date format in our system."}
        
    return {"eligible": True, "reason": "The item is within the 30-day return window and is not a sale item."}

def create_return(order_id: str) -> dict:
    """
    Initiate a return for a given order.
    
    Args:
        order_id: The ID of the order to return.
        
    Returns:
        A dictionary containing the return status and return ID if successful.
    """
    eligibility = check_return_eligibility(order_id)
    
    if not eligibility["eligible"]:
        return {
            "success": False,
            "message": f"Cannot create return: {eligibility['reason']}"
        }
        
    # In a real system, we would write this to a database
    return {
        "success": True,
        "return_id": f"RET-{order_id}",
        "message": "Return successfully created. A return label will be emailed to you."
    }

def create_exchange(order_id: str, new_item: str) -> dict:
    """
    Initiate an exchange for a given order to get a new item.
    
    Args:
        order_id: The ID of the order to exchange.
        new_item: The name or description of the new item requested.
        
    Returns:
        A dictionary containing the exchange status and exchange ID if successful.
    """
    eligibility = check_return_eligibility(order_id)
    
    if not eligibility["eligible"]:
        return {
            "success": False,
            "message": f"Cannot create exchange: {eligibility['reason']}"
        }
        
    return {
        "success": True,
        "exchange_id": f"EXC-{order_id}",
        "message": f"Exchange for '{new_item}' successfully initiated. Instructions will be emailed to you."
    }

def escalate_to_human(order_id: Optional[str], issue: str, order_status: Optional[str], actions_taken: str, reason: str) -> dict:
    """
    Escalate the customer's issue to a human support agent.
    
    Args:
        order_id: The ID of the order involved, if applicable.
        issue: A brief description of the customer's problem.
        order_status: The current status of the order, if applicable.
        actions_taken: What steps the AI agent has already tried.
        reason: Why the issue needs human intervention.
        
    Returns:
        A structured summary dictionary for the human agent.
    """
    return {
        "escalation_id": "ESC-" + (order_id if order_id else "GENERIC"),
        "status": "Escalated to Human Agent",
        "details": {
            "order_id": order_id,
            "issue": issue,
            "order_status": order_status,
            "actions_taken": actions_taken,
            "reason": reason
        },
        "message": "I have escalated this issue to our human support team. An agent will contact you shortly."
    }

if __name__ == "__main__":
    # Simple manual tests
    print("--- Test get_order ---")
    print(get_order("ORD101")) # Real order
    print(get_order("ORD999")) # Fake order
    
    print("\n--- Test search_policy ---")
    print(search_policy("I want to return an item"))
    print("---")
    print(search_policy("What is the exchange policy?"))
    
    print("\n--- Test check_return_eligibility ---")
    print("ORD101 (Delivered, in window):", check_return_eligibility("ORD101"))
    print("ORD103 (Delivered, out of window):", check_return_eligibility("ORD103"))
    print("ORD105 (Delivered, sale item):", check_return_eligibility("ORD105"))
    
    print("\n--- Test create_return ---")
    print(create_return("ORD101"))
    print(create_return("ORD105"))
    
    print("\n--- Test escalate_to_human ---")
    print(escalate_to_human("ORD102", "Package says delivered but missing", "delivered", "Checked tracking", "Customer states missing after 48h"))
