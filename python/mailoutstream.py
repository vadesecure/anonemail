from os.path import join
from hashlib import md5
from smtplib import SMTP

class MailOutStream():
    logger = None
    is_sampled = False
    
    def __init__(self, is_smpl, logger=None):
        self.logger = logger
        self.is_sampled = is_smpl
    
    def send_success(self, message):
        """Send the message to the success output stream.
        :param message: the anonymized mail
        """
        if self.logger is not None:
            self.logger.debug("successfuly anonymized message from {} to {}".format(message["From"], message["To"]))
    
    def send_error(self, message):
        """Send the message to the error output stream.
        :param message: the anonymized mail
        """
        if self.logger is not None:
            self.logger.info("error while message anonymisation")
    
    def send_sample(self, message):
        """Send the sample to the success output stream, to create a mail corpus for example.
        :param message: the anonymized mail
        """
        if self.logger is not None:
            self.logger.debug("message was sampled")


class FileMailOutStream(MailOutStream):
    success_directory_path = ""
    sample_directory_path = ""
    error_directory_path = ""
    is_sampled = False
    
    def __init__(self, success_directory_path, sample_directory_path="", error_directory_path="", is_sampled=False, logger=None):
        super().__init__(is_sampled, logger)
        self.success_directory_path = success_directory_path
        self.sample_directory_path = sample_directory_path
        self.error_directory_path = error_directory_path
    
    def send_success(self, message):
        _hasher = md5()
        _hasher.update(message)
        file_path = join(self.success_directory_path, _hasher.hexdigest() + ".eml")
        with open(file_path, "wb") as success_file:
            success_file.write(message)
        super().send_success(message)

    def send_error(self, message):
        _hasher = md5()
        _hasher.update(message)
        file_path = join(self.error_directory_path, _hasher.hexdigest() + ".eml")
        with open(file_path, "w") as error_file:
            error_file.write(message)
        super().send_error(message)

    def send_sample(self, message):
        if not self.is_sampled:
            return
        _hasher = md5()
        _hasher.update(message)
        file_path = join(self.sample_directory_path, _hasher.hexdigest() + ".eml")
        with open(file_path, "wb") as sample_file:
            error_file.write(message)
        super().send_sample(message)


class SMTPMailOutStream(MailOutStream):
    from_addr = ""
    error_addr = ""
    smpl_addr = ""
    to_addr = ""
    smtp_srv = ""
    smtp_port = 25

    def __send_message(self, dest, message_str):
        server = SMTP(self.smtp_srv)
        server.sendmail(self.from_addr, dest, message_str)
        s.quit()
    
    def __init__(self, from_addr, to_addr, error_addr, smpl_addr, smtp_srv, is_sampled=False, logger=None):
        super().__init__(is_sampled, logger)
        self.from_addr = from_addr
        self.to_addr = to_addr
        self.error_addr = error_addr
        self.smpl_addr = smpl_addr
        self.smtp_srv = smtp_srv
    
    def send_success(self, message):
        self.__send_message(self.to_addr, message)
        super().send_success()
    
    def send_error(self, message):
        self.__send_message(self.error_addr, message)
        super().send_error()
    
    def send_sample(self, message):
        if not self.is_sampled:
            return
        self.__send_message(self.smpl_addr, message)
        super().send_sample()
