import hashlib


class UserLogic:
    HASH_FORMAT = "{method}${iterations}${hash}"
    HASH_METHOD = "sha256"
    HASH_ITERATIONS = 100

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

    @staticmethod
    def hash_password(password: str, method: str = HASH_METHOD, iterations: int = HASH_ITERATIONS) -> str:
        hash = None
        if method == "sha256":
            hash = hashlib.sha256()
        else:
            hash = hashlib.md5()

        hash.update(password.encode())
        for _ in range(max(iterations - 1, 0)): # technically already does one iteration when creating hash
            hash.update(hash.digest())

        return UserLogic.HASH_FORMAT.format(method = method, iterations = iterations, hash = hash.hexdigest())

    @staticmethod
    def compare_password(input: str, saved: str) -> bool:
        metadata: list[str] = saved.split('$')
        input_digest: str

        if len(metadata) == 1: # doesn't use the new format, so assume it's legacy/MD5
            _, _, input_digest = UserLogic.hash_password(input, method = "md5", iterations = 1).split('$')
        else:
            method, iterations, _ = metadata
            input_digest = UserLogic.hash_password(input, method = method, iterations = int(iterations))

        print(input_digest, saved)
        return input_digest == saved
