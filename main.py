from flask import Flask, request, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from contact import Contact, LinkPrecedence, Base
import logging
from sqlalchemy import inspect

app = Flask(__name__)

engine = create_engine("sqlite:///contacts.db")
Session = sessionmaker(bind=engine)

logging.basicConfig(level=logging.INFO)
logging.info("Creating tables...")
Base.metadata.create_all(engine)
logging.info("Tables created successfully.")

inspector = inspect(engine)
print("Tables in the database:", inspector.get_table_names())

@app.route("/identify", methods=["POST"])
def identify():
    session = Session()
    data = request.json
    email = data.get("email")
    phone_number = data.get("phoneNumber")

    matching_contacts = session.query(Contact).filter(
        (Contact.email == email) | (Contact.phoneNumber == phone_number)
    ).all()

    if not matching_contacts:
        new_contact = Contact(email=email, phoneNumber=phone_number, linkPrecedence=LinkPrecedence.PRIMARY)
        session.add(new_contact)
        session.commit()

        response = {
            "primaryContactId": new_contact.id,
            "emails": [new_contact.email],
            "phoneNumbers": [new_contact.phoneNumber],
            "secondaryContactIds": []
        }
    else:
        primary_contact = None
        secondary_contact_ids = []
        emails = set()
        phone_numbers = set()

        for contact in matching_contacts:
            if contact.linkPrecedence == LinkPrecedence.PRIMARY:
                primary_contact = contact
            else:
                secondary_contact_ids.append(contact.id)
            if contact.email:
                emails.add(contact.email)
            if contact.phoneNumber:
                phone_numbers.add(contact.phoneNumber)

        if primary_contact:
            if email and email not in emails:
                primary_contact.email = email
            if phone_number and phone_number not in phone_numbers:
                primary_contact.phoneNumber = phone_number
            session.commit()

            response = {
                "primaryContactId": primary_contact.id,
                "emails": list(emails),
                "phoneNumbers": list(phone_numbers),
                "secondaryContactIds": secondary_contact_ids
            }
        else:
            new_primary = matching_contacts[0]
            new_primary.linkPrecedence = LinkPrecedence.PRIMARY
            session.commit()

            primary_contact = new_primary
            secondary_contact_ids = [contact.id for contact in matching_contacts if contact.id != new_primary.id]

            response = {
                "primaryContactId": primary_contact.id,
                "emails": list(emails),
                "phoneNumbers": list(phone_numbers),
                "secondaryContactIds": secondary_contact_ids
            }

    session.close()
    return jsonify(response), 200

if __name__ == "__main__":
    app.run(debug=True)




'''
Method Invoktion:

Invoke-WebRequest -Uri http://127.0.0.1:5000/identify -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"email": "test@example.com", "phoneNumber": "1234567890"}'

'''