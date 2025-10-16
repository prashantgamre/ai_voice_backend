import logging
import token
from livekit.agents import function_tool, RunContext
from numpy import number
import requests
import json
from Zoho_token import get_access_token



@function_tool()
async def products_details(
    context: RunContext,
    products:str
    ):
    """Get products details from database."""

    try:
        token = get_access_token()
        headers = {
    "Authorization": f"Zoho-oauthtoken {token}",
    } # 1000.d9ee65f2bbb86efb9d96fefa55c41d9c.9ff07cd9dc39280ea5a4d5ddc5efde94
        response = requests.get(f"https://www.zohoapis.in/crm/v8/Products?fields=Product_Name={products},Unit_Price,Product_Name,Color,Storage", headers=headers)
        if response.status_code == 200:
            logging.info(f"Products details for {products} retrieved : {response.json()}")
            return response.json()
        else:
            logging.error(f"Error getting products details for {products}: {response.json()}")
            return None
    except Exception as e:
        logging.error(f"Error getting products details: {e}")
        return None

@function_tool()
async def user_details(
    context: RunContext,
    number:str
    ):
    """Get user details from database."""

    try:
        token = get_access_token()
        headers = {
    "Authorization": f"Zoho-oauthtoken {token}",
    } # 1000.d9ee65f2bbb86efb9d96fefa55c41d9c.9ff07cd9dc39280ea5a4d5ddc5efde94
        response = requests.get(f"https://www.zohoapis.in/crm/v8/Leads/search?phone={number}", headers=headers)
        if response.status_code == 200:
            logging.info(f"User details for {number} retrieved : {response.json()}")
            return response.json()
        else:
            logging.error(f"Error getting user details for {number}: {response.json()}")
            return None
    except Exception as e:
        logging.error(f"Error getting user details: {e}")
        return None


@function_tool()
async def Record_details(
    context: RunContext,
    LayoutID:str,
    Lead_Source:str,
    Company:str,
    Last_Name:str,
    First_Name:str,
    State:str,
    number:str,
    products:str,
    ):
    """add user details to database in given layout ID - 1029750000000000167 ."""

    try:
        token = get_access_token()
        url = "https://www.zohoapis.in/crm/v8/Leads"
        headers = {
    "Authorization": f"Zoho-oauthtoken {token}",
    "Content-Type": "application/json",
    }
        data = {
    "data": [
        {
            "Layout": {
                "id": LayoutID
            },
            "Lead_Source": Lead_Source,
            "Company": Company,
            "Last_Name": Last_Name,
            "First_Name": First_Name,
            "State": State,
            "Phone": number,
            "Products": products,
        },
    ]
}
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 201:
            logging.info(f"User details for {number} retrieved : {response.json()}")
            return response.json()
        else:
            logging.error(f"Error getting user details for {number}: {response.json()}")
            return None
    except Exception as e:
        logging.error(f"Error getting user details: {e}")
        return None

@function_tool()
async def Solutions_details(
    context: RunContext,
    Solutions:str
    ):
    """Get Solutions details from database."""

    try:
        token = get_access_token()
        headers = {
    "Authorization": f"Zoho-oauthtoken {token}",
    } # 1000.d9ee65f2bbb86efb9d96fefa55c41d9c.9ff07cd9dc39280ea5a4d5ddc5efde94
        response = requests.get(f"https://www.zohoapis.in/crm/v8/Solutions?fields=Solution_Title,Question,Answer", headers=headers)
        if response.status_code == 200:
            logging.info(f"Solutions details for {Solutions} retrieved : {response.json()}")
            return response.json()
        else:
            logging.error(f"Error getting Solutions details for {Solutions}: {response.json()}")
            return None
    except Exception as e:
        logging.error(f"Error getting Solutions details: {e}")
        return None

@function_tool()
async def Add_Issue_Cases(
    context: RunContext,
    Issue:str,
    Owner_Id:60050148252,
    Staus:"Escalated",
    Email:str,
    Phone:str,
    Product:str,
    Description:str,
    ):
    """Add Issue details in database."""

    try:
        token = get_access_token()
        headers = {"Authorization": f"Zoho-oauthtoken {token}"}
        data = {
        "data": [
            {
            "Owner": {
                "id": Owner_Id
            },
            "Status": Staus,
            "Email": Email,
            "Phone": Phone,
            "Product": Product,
            "Description": Description,
        }
    ]
}
        response = requests.post(f"https://www.zohoapis.in/crm/v8/Cases", headers=headers,data=json.dumps(data))
        if response.status_code == 201:
            logging.info(f"Issue details for {Issue} retrieved : {response.json()}")
            return response.json()
        else:
            logging.error(f"Error getting Issue details for {Issue}: {response.json()}")
            return None
    except Exception as e:
        logging.error(f"Error getting Issue details: {e}")
        return None