import pytest
from LogicLayer.userLogic import UserLogic

def testCheckPassword():
    password_without_uppercase = "password321!"
    password_without_lowercase = "PASSWORD321!"
    password_without_numbers = "Password!"
    password_without_symbols = "Password321"

    correct_password = "Password321!"
    short_password = "Pas1!"

    result_password_without_uppercase = UserLogic.CheckPassword(password_without_uppercase)
    assert result_password_without_uppercase == 1

    result_password_without_lowercase = UserLogic.CheckPassword(password_without_lowercase)
    assert result_password_without_lowercase == 2

    result_password_without_numbers = UserLogic.CheckPassword(password_without_numbers)
    assert result_password_without_numbers == 3

    result_password_without_symbols = UserLogic.CheckPassword(password_without_symbols)
    assert result_password_without_symbols == 4

    result_correct_password = UserLogic.CheckPassword(correct_password)
    assert result_correct_password == 5

    result_short_password = UserLogic.CheckPassword(short_password)
    assert result_short_password == 0

def testCheckName():
    name_without_lastname = "Sina"
    name_with_number = "Sina3 Hashemy"
    name_with_symbol = "Sina@ Hashemy"
    correct_name = "Sina Hashemy"

    result_name_without_lastname = UserLogic.CheckName(name_without_lastname)
    assert result_name_without_lastname == 0

    result_name_with_number = UserLogic.CheckName(name_with_number)
    assert result_name_with_number == 1

    result_name_with_symbol = UserLogic.CheckName(name_with_symbol)
    assert result_name_with_symbol == 1

    result_correct_name = UserLogic.CheckName(correct_name)
    assert result_correct_name == 2

def testCheckEmail():
    email_with_space = "sina h@gmail.com"
    email_without_ad = "sinahgmail.com"
    email_with_two_ad = "sinah@@gmail.com"
    email_without_name = "@gmail.com"
    email_without_domain = "sinah@"
    email_without_dot_in_domain = "sinah@gmailcom"
    correct_email = "sina@gmail.com"

    result_email_with_space = UserLogic.CheckEmail(email_with_space)
    assert result_email_with_space == 0

    result_email_without_ad = UserLogic.CheckEmail(email_without_ad)
    assert result_email_without_ad == 1

    result_email_with_two_ad = UserLogic.CheckEmail(email_with_two_ad)
    assert result_email_with_two_ad == 1

    result_email_without_name = UserLogic.CheckEmail(email_without_name)
    assert result_email_without_name == 2

    result_email_without_domain = UserLogic.CheckEmail(email_without_domain)
    assert result_email_without_domain == 3

    result_email_without_dot_in_domain = UserLogic.CheckEmail(email_without_dot_in_domain)
    assert result_email_without_dot_in_domain == 3

    result_correct_email = UserLogic.CheckEmail(correct_email)
    assert result_correct_email == 5

def testCheckPhone():
    phone_number_with_letter = "+d10222939422"
    phone_number_with_symbol = "+@10222939422"
    phone_number_with_letter_no_plus = "d10222932"
    phone_number_with_symbol_no_plus = "@10222932"
    phone_number_wrong_length = "+31022293942"
    phone_number_wrong_length_no_plus = "31022293"
    correct_phone_number = "+310222939422"
    correct_phone_number_no_plus = "222939422"

    result_phone_number_with_letter = UserLogic.CheckPhone(phone_number_with_letter)
    assert result_phone_number_with_letter == 0

    result_phone_number_with_symbol = UserLogic.CheckPhone(phone_number_with_symbol)
    assert result_phone_number_with_symbol == 0

    result_phone_number_with_letter_no_plus = UserLogic.CheckPhone(phone_number_with_letter_no_plus)
    assert result_phone_number_with_letter_no_plus == 0

    result_phone_number_with_symbol_no_plus = UserLogic.CheckPhone(phone_number_with_symbol_no_plus)
    assert result_phone_number_with_symbol_no_plus == 0

    result_phone_number_wrong_length = UserLogic.CheckPhone(phone_number_wrong_length)
    assert result_phone_number_wrong_length == 0

    result_phone_number_wrong_length_no_plus = UserLogic.CheckPhone(phone_number_wrong_length_no_plus)
    assert result_phone_number_wrong_length_no_plus == 0

    result_correct_phone_number = UserLogic.CheckPhone(correct_phone_number)
    assert result_correct_phone_number == 2

    result_correct_phone_number_no_plus = UserLogic.CheckPhone(correct_phone_number_no_plus)
    assert result_correct_phone_number_no_plus == 1