from app import create_app, db
from app.models.teacher import Department

def main():
    app = create_app('default')
    with app.app_context():
        try:
            # Create a test department
            dept = Department(
                name="测试院系",
                code="TEST001",
                # contact="test@example.com",  # Temporarily removed
                description="This is a test department"
            )
            
            db.session.add(dept)
            db.session.commit()
            
            print(f"Successfully created department with id: {dept.id}")
            
            # Verify the department was created
            dept_check = Department.query.get(dept.id)
            if dept_check:
                print(f"Department found: {dept_check.name}")
                # print(f"Contact: {dept_check.contact}")  # Temporarily removed
            else:
                print("Failed to retrieve the department")
                
        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    main() 