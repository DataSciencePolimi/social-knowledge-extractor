
class Mail()
    def __init__(self):
        pass
    
    def send(self, db,experiment_id):

        experiment = db.getExperiment(experiment_id)

        sender = 'YOUR GMAIL ADDRESS'
        gmail_password = 'YOUR GMAIL PASSWORD'
        recipients = [experiment.email]
    
        # Create the enclosing (outer) message
        outer = MIMEMultipart()
        outer['Subject'] = 'Results'
        outer['To'] = COMMASPACE.join(recipients)
        outer['From'] = sender