from collections import UserDict
from datetime import datetime, date, timedelta

# Базовий клас для полів запису.
class Field:
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)

# Клас для зберігання імені контакту. 
class Name(Field):
    pass

# Клас для зберігання номера телефону з валідацією.
class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise Exception('The number must contain 10 digits.')
        super().__init__(value)

    def __repr__(self):
        return f'{self.value}'
    
# Клас для зберігання дати народження з валідацією.
class Birthday(Field):
    def __init__(self, value):
        self.value = value
        try:
            self.value = datetime.strptime(value, '%d.%m.%Y').date()
        except Exception:
            raise Exception("Invalid date format. Use DD.MM.YYYY")

# Клас для зберігання інформації про контакт та методами маніпуляції з нею.
class Record:
    def __init__(self, name):
        self.name = Name(name) 
        self.phones = []       
        self.birthday = None   

    def add_phone(self, phone):        
        self.phones.append(Phone(phone))

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def remove_phone(self, phone):
        self.phones.remove(self.find_phone(phone))
        
    def edit_phone(self, phone, new_phone):
        if self.find_phone(phone):
            self.add_phone(new_phone)
            self.remove_phone(phone) 
        else:
            raise Exception(f'The contact {self.name.value.capitalize()} does not contain the specified number - {phone}.')

    def find_phone(self, phone):
        for i in self.phones:
            if i.value == phone:
                return i

    def __str__(self):    # реалізація user-friendly виводу
        return f"Contact name: {self.name.value.capitalize()}, Phones: {'; '.join(p.value for p in self.phones)}, Birthday: {self.birthday}"

# Клас для зберігання та управління записами.
class AddressBook(UserDict):

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        for i in self.data.keys():
            if i.lower() == name.lower():
                return self.data[i]

    def adjust_for_weekend(self, birthday):
        if birthday.weekday() >= 5:
            return self.find_next_weekday(birthday, 0)
        return birthday
    
    def find_next_weekday(self, start_date, weekday):
        days_ahead = weekday - start_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return start_date + timedelta(days=days_ahead)
    
    def date_to_string(self, date):
        return date.strftime("%d.%m.%Y")
    
    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        users = []
        today = datetime.today().date()

        for i in self.data.values():
            user = {}
            user['name'] = i.name.value
            user['birthday'] = i.birthday.value
            users.append(user)

        for user in users:
            birthday_this_year = user["birthday"].replace(year=today.year)
            if birthday_this_year < today:
                birthday_next_year = birthday_this_year.replace(year=birthday_this_year.year + 1)
                if (birthday_next_year - today).days <= days:
                    birthday_this_year = birthday_next_year

            if 0 <= (birthday_this_year - today).days <= days:
                self.adjust_for_weekend(birthday_this_year)
                birthday_this_year = self.adjust_for_weekend(birthday_this_year)
                congratulation_date_str = self.date_to_string(birthday_this_year)
                upcoming_birthdays.append({"Name": user["name"].capitalize(), "Congratulation date": congratulation_date_str})
        if upcoming_birthdays:
            return upcoming_birthdays
        else:
            raise Exception('No contacts to greet.')

    
    def __str__(self):  # реалізація user-friendly виводу
            return "\n".join(str(r) for r in self.data.values())

# Декоратор для обробки помилок введення
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return 'Invalid input data.'
        except AttributeError:
            return 'There is no such contact.'
        except TypeError:
            return 'TypeError'
        except Exception as error:
            return error
    return inner

# Парсер команд
@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

# Handler
@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = 'Contact updated.'
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = 'Contact added.'
    if phone:
        record.add_phone(phone)
    return message

@input_error  
def change_contact(args, book: AddressBook):
    name, phone, new_phone, *_ = args
    record = book.find(name)
    record.edit_phone(phone, new_phone)
    return 'Contact updated.'

@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    return f"{name.capitalize()}'s phones: {record.phones}"

def show_all(book: AddressBook):
    return book

@input_error
def add_birthday(args, book):
    name, birthday, *_ = args
    record = book.find(name)
    record.add_birthday(birthday)
    return 'Birthday added.'

@input_error
def show_birthday(args, book):
    name, *_ = args
    record = book.find(name)
    return f"{name.capitalize()}'s birthday - {record.birthday}"

@input_error
def birthdays(book):
    return book.get_upcoming_birthdays()


# Цикл взаємодії з користувачем
def main():

    book = AddressBook()
    print('Welcome to the assistant bot!')

    while True:
    
        user_input = input('Enter a command:')
        command, *args = parse_input(user_input)

        if command == 'hello':
            print('How can I help you?')

        elif command == 'add':
            print(add_contact(args, book))
    
        elif command == 'change':
            print(change_contact(args, book))

        elif command == 'phone':
            print(show_phone(args, book))

        elif command == 'all':
            print(show_all(book))
            
        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

            
        elif command in ['close', 'exit']:
            print('Good bye!')
            break 

        else: 
            print('Invalid command.')
    
if __name__ == '__main__':
    main()



