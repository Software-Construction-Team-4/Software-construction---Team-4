from LogicLayer.userLogic import UserLogic
import hashlib


def get_digest(hashed_password: str) -> str:
    # the hash_password method stores the password with metadata
    return hashed_password.split('$')[-1]


def test_hashing_one_iteration() -> None:
    password: str = "test123"

    digest_sha256_manual: str = hashlib.sha256(password.encode()).hexdigest()
    digest_sha256_logic: str = get_digest(UserLogic.hash_password(password, method = "sha256", iterations = 1))

    digest_md5_manual: str = hashlib.md5(password.encode()).hexdigest()
    digest_md5_logic: str = get_digest(UserLogic.hash_password(password, method = "md5", iterations = 1))

    assert digest_sha256_manual == digest_sha256_logic
    assert digest_md5_manual == digest_md5_logic


def test_hashing_hundred_iteration() -> None:
    password: str = "VeryStrongPassword"
    iterations: int = 100

    hash_manual = hashlib.sha256()
    hash_manual.update(password.encode())
    for _ in range(iterations - 1):
        hash_manual.update(hash_manual.digest())

    digest_manual: str = hash_manual.hexdigest()
    digest_logic: str = get_digest(UserLogic.hash_password(password = password, method = "sha256", iterations = iterations))

    assert digest_manual == digest_logic


def test_comparison() -> None:
    input_password: str = "Gamb!tNeverFo1ds"
    saved_password: str = UserLogic.hash_password(password = input_password, method = "sha256", iterations = 100)

    assert UserLogic.compare_password(input_password, saved_password)


def test_comparison_backwards_compatibility() -> None:
    saved_password: str = "hunter2"
    saved_password_digest: str = hashlib.md5(saved_password.encode()).hexdigest()

    input_password_correct: str = "hunter2"
    input_password_incorrect: str = "warrior4"

    assert UserLogic.compare_password(input_password_correct, saved_password_digest) == True
    assert UserLogic.compare_password(input_password_incorrect, saved_password_digest) == False
