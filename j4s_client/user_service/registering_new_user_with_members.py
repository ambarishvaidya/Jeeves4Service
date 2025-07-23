from services.user_service.app.di.containers import ServiceFactory
from services.user_service.app.dto.registration import RegisterUserRequest
from services.user_service.app.dto.user import AddUserRequest
from datetime import date

def register_new_user_with_members():
    """Register Virendra Vaidya with 4 family members"""
    
    try:
        # Get the registration service
        register_service = ServiceFactory.get_register_user_service()
        
        # Create additional family members
        additional_users = [
            AddUserRequest(
                first_name="Vasanti1",
                last_name="Vaidya1", 
                email="vasantivv1@gmail.com",                
                dob=date(1957, 11, 8)
            ),
            AddUserRequest(
                first_name="Aditya1",
                last_name="Vaidya1",
                email="aditya.vaidya1@gmail.com",                 
                dob=date(1971, 5, 30)          
            )           
        ]
        
        # Create main registration request for Virendra (admin)
        request = RegisterUserRequest(
            first_name="Virendra1",
            last_name="Vaidya1",
            email="vvvaidya1@gmail.com",
            password="v1v2v3v4v5&",
            dob=date(1945, 9, 9),
            additional_users=additional_users
        )
        
        print("Starting registration for Virendra Vaidya with 4 family members...")
        print(f"Main User: {request.first_name} {request.last_name} ({request.email})")
        print(f"Family Members: {len(additional_users)}")
        for i, user in enumerate(additional_users, 1):
            print(f"  {i}. {user.first_name} {user.last_name} ({user.email})")
        
        # Register the user with family members
        response = register_service.register_user(request)
        
        print(f"\n✅ Registration Successful!")
        print(f"Main User ID: {response.user_id}")
        print(f"Message: {response.message}")
        
        return response
        
    except ValueError as ve:
        print(f"❌ Validation Error: {ve}")
        return None
        
    except Exception as e:
        print(f"❌ Registration Failed: {e}")
        return None

if __name__ == "__main__":
    register_new_user_with_members()
