from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from db import get_hospital_db_connection

router = APIRouter()

@router.get("/{patient_id}")
def book_appointment(
    patient_id: str,
    fetch_filters: Optional[bool] = Query(False),
    state: Optional[str] = '',
    city: Optional[str] = '',
    zip: Optional[str] = '',
    county: Optional[str] = '',
    type: Optional[str] = '',
    ownership: Optional[str] = '',
    emergency: Optional[str] = '',
    rating: Optional[str] = ''
):
    if fetch_filters:
        return fetch_filter_data()

    try:
        cnxn = get_hospital_db_connection()
        cursor = cnxn.cursor()

        query = """
            SELECT TOP 10 [Facility_ID], [Facility_Name], [Address], [City_Town], [State], [ZIP_Code], [County_Parish], 
            [Telephone_Number], [Hospital_Type], [Hospital_Ownership], [Emergency_Services], [Hospital_overall_rating]
            FROM hospital
            WHERE 
                ([State] = ? OR ? = '') AND
                ([City_Town] = ? OR ? = '') AND
                ([ZIP_Code] = ? OR ? = '') AND
                ([County_Parish] = ? OR ? = '') AND
                ([Hospital_Type] = ? OR ? = '') AND
                ([Hospital_Ownership] = ? OR ? = '') AND
                ([Emergency_Services] = ? OR ? = '') AND
                ([Hospital_overall_rating] = ? OR ? = '')
            ORDER BY [Facility_Name] ASC
        """

        filters = [state, state, city, city, zip, zip, county, county,
                   type, type, ownership, ownership, emergency, emergency,
                   rating, rating]

        cursor.execute(query, filters)
        hospitals = cursor.fetchall()
        hospital_data = [dict(zip([column[0] for column in cursor.description], row)) for row in hospitals]
        return hospital_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching hospital data: {str(e)}")
    finally:
        cursor.close()
        cnxn.close()


@router.get("/filters/")
def fetch_filter_data():
    try:
        cnxn = get_hospital_db_connection()
        cursor = cnxn.cursor()

        cursor.execute("SELECT DISTINCT [State] FROM hospital")
        states = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT [City_Town] FROM hospital")
        cities = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT [County_Parish] FROM hospital")
        counties = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT [Hospital_Type] FROM hospital")
        types = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT [Hospital_Ownership] FROM hospital")
        ownerships = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT [Emergency_Services] FROM hospital")
        emergencies = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT [Hospital_overall_rating] FROM hospital")
        ratings = [row[0] for row in cursor.fetchall()]

        return {
            "states": states,
            "cities": cities,
            "counties": counties,
            "types": types,
            "ownerships": ownerships,
            "emergencies": emergencies,
            "ratings": ratings
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching filter data: {str(e)}")
    finally:
        cursor.close()
        cnxn.close()
