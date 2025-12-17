class UserLogic:
    def CheckPassword(password):
        if len(password) < 8:
            return 0

        has_upper = False
        has_lower = False
        has_digit = False
        has_special = False

        for char in password:
            if char.isupper():
                has_upper = True
            elif char.islower():
                has_lower = True
            elif char.isdigit():
                has_digit = True
            else:
                has_special = True

        if has_upper == False:
            return 1
        elif has_lower == False:
            return 2
        elif has_digit == False:
            return 3
        elif has_special == False:
            return 4
        else:
            return 5
        
    def CheckName(name):
        listName = name.strip().split()
        if len(listName) < 2:
            return 0

        for char in name:
            if not (char.isalpha() or char == " "):
                return 1

        return 2

    def CheckEmail(email):
        email = email.strip()
        
        if " " in email:
            return 0

        if email.count("@") != 1:
            return 1

        namePart, domainPart = email.split("@")

        if not namePart:
            return 2

        if not domainPart or "." not in domainPart:
            return 3

        return 5
    
    def CheckPhone(phone):
        phone = phone.strip()

        if phone.startswith("+"):
            if not phone[1:].isdigit():
                return 0
            if len(phone[1:]) != 12:
                return 0
            return 2

        elif phone.isdigit():
            if len(phone) != 9:
                return 0
            return 1

        else:
            return 0