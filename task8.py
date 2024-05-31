
from datetime import datetime, timedelta
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if len(value) != 10 or not value.isdigit():
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        phones_list_str = [str(phone) for phone in self.phones]

        if phone_number in phones_list_str:
            raise ValueError("Phone is alredy in the list")
        
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone):
        self.phones.remove(self.find_phone(phone))

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        print("Phone number not found.")

    def find_phone(self, phone):
        for number in self.phones:
            if number.value == phone:
                return phone
        
        return f"Phone {phone} is not in the list"

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(str(p) for p in self.phones)}, birthday: {self.birthday}"


class AddressBook(dict):
    def add_record(self, record):
        self[record.name.value] = record

    def find(self, name):
        return self.get(name)

    def delete(self, name):
        if name in self:
            del self[name]

    def get_upcoming_birthdays(self, days=7):
        current_date = datetime.today().date()
        upcoming_birthdays = []
        for record in self.values():
            if record.birthday:
                birthday_date = record.birthday.value
                birthday_this_year = birthday_date.replace(year=current_date.year)
            if birthday_this_year < current_date:
                birthday_this_year = birthday_this_year.replace(year=current_date.year + 1)
            days_difference = (birthday_this_year - current_date).days
            if 0 <= days_difference <= days:
                adjusted_birthday = adjust_for_weekend(birthday_this_year)
                upcoming_birthdays.append(
                    {
                    'name': record.name.value.title(),
                    'congratulation_date': str(adjusted_birthday)
                    }
                    )
        return upcoming_birthdays

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"ValueError: {str(e)}\nPlease provide correct arguments."
        except KeyError as k:
            return f"KeyError: {str(k)}\nEnter a valid command again\n"
        except IndexError as i:
            return f"IndexError: {str(i)} Invalid number of arguments."
        
    return inner

@input_error
def add_contact(args, book):
    if len(args) < 2:
        raise ValueError("Give me name and phone please, try again.")
    name, phone = args[:2]
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    record.add_phone(phone)
    return message


@input_error
def change_phone(args, book):
    if len(args) < 2:
        raise ValueError("Give me name and phone please, try again.")
    name, phone = args
    record = book.find(name)
    if record:
        record.add_phone(phone)
        return "Phone number updated."
    else:
        return "Contact not found."


@input_error
def show_phone(args, book):
    if len(args) < 1:
        raise ValueError("Wrong command to show users phone. Please enter command 'phone' and 'name'")
    name = args[0]
    record = book.find(name)
    if record:
        phones = ', '.join(str(p) for p in record.phones)
        return f"Phone number: {phones}" if phones else "No phone numbers found."
    else:
        return "Contact not found."

@input_error
def show_all(book:AddressBook):
    records_info = "\n".join(str(record) for record in book.values())
    return records_info if records_info else "No contacts found."

@input_error
def add_birthday(args, book:AddressBook):
    if len(args) < 2:
        raise ValueError("Wrong command to add birthday. Please enter command 'add-birthday' + 'name' + 'date of birthday'")
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    else:
        return "Contact not found."

@input_error
def show_birthday(args, book:AddressBook):
    if len(args) < 1:
        raise ValueError("Wrong command to show birthday. Please enter command 'show-birthday' and 'name'")
    name = args[0]
    record = book.find(name)
    if record:
        if record.birthday:
            return f"Birthday: {record.birthday}"
        else:
            return "Birthday not set."
    else:
        return "Contact not found."

def adjust_for_weekend(date):
    weekday = date.weekday()
    if weekday == 5:  # якщо др випадає на суботу
        return date + timedelta(days=2)
    elif weekday == 6:  # якщо др випадає на неділю
        return date + timedelta(days=1)
    return date
    
def birthdays(book:AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "Upcoming birthdays: \n" + "\n".join(str(record) for record in upcoming_birthdays).replace('{', '').replace('}', '').replace("'", "")
    else:
        return "No upcoming birthdays."

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        if not user_input: 
            print("Please enter a command.")
            continue
        command, *args = parse_input(user_input)

        match command:
            case "close" | "exit":
                print("Good bye!")
                save_data(book)
                break
            case "hello":         print("How can I help you?")
            case "add":           print(add_contact(args, book))
            case "change":        print(change_phone(args, book))
            case "phone":         print(show_phone(args, book))
            case "all":           print(show_all(book))
            case "add-birthday":  print(add_birthday(args, book))
            case "show-birthday": print(show_birthday(args, book))
            case "birthdays":     print(birthdays(book))
            case _:               print("Invalid command, please try again. \nIf you want to exit the bot : type 'exit' or 'close'\n ")

if __name__ == "__main__":
    main()
