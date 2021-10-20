# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import logging
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s:%(levelname)s:%(module)s:%(lineno)d:%(message)s'
)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


async def create_account_verification(from_email, to_emails, data: dict):
    """Gửi thông báo xác nhận tài khoản mới tạo
    Args:
        from_email (str): Email gửi
        to_email (list, tuple, str): Email nhận hoặc danh sách email nhận

    Returns:
        True if sent successfully else False
    """
    message = Mail(
        from_email=from_email,
        to_emails=to_emails)
    message.dynamic_template_data = data
    message.template_id = "d-bfe931e480ef4069acf79b2bb5aa76fe" #TODO thay thế template id bằng dynamic template id trên sendgrid
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        logger.info(response.status_code)
        logger.info(response.body)
        logger.info(response.headers)
    except Exception as e:
        logger.info(e.message)
        return False
    return True


async def send_reset_password_email(from_email, to_emails, data: dict):
    """Gửi email reset mật khẩu tài khoản
    Args:
        from_email (str): Email gửi
        to_email (list, tuple, str): Email nhận hoặc danh sách email nhận

    Returns:
        True if sent successfully else False
    """
    message = Mail(
        from_email=from_email,
        to_emails=to_emails)
    message.dynamic_template_data = data
    message.template_id = "d-e1601fc60c5c4d74b7af28e24006950b" #TODO thay thế template id bằng dynamic template id trên sendgrid
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        logger.info(response.status_code)
        logger.info(response.body)
        logger.info(response.headers)
    except Exception as e:
        logger.info(e.message)
        return False
    return True
