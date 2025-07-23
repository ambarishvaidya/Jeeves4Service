from services.user_service.app.di.containers import ServiceFactory
from services.user_service.app.dto.registration import RegisterUserRequest
from datetime import date

def register_new_user():
    register_service = ServiceFactory.get_register_user_service()
    request = RegisterUserRequest(
        first_name="Vaijayanti",
        last_name="Vaidya",
        email="vaijayanti.vaidya@gmail.com",
        password="jeeves4service123",
        dob=date(1976, 4, 5),
        additional_users=[]  
    )
    response = register_service.register_user(request)
    print(response)

if __name__ == "__main__":
    register_new_user()    
