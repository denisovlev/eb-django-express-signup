from django.db import models
import boto3
import os
import logging

STARTUP_SIGNUP_TABLE = os.environ['STARTUP_SIGNUP_TABLE']
AWS_REGION = os.environ['AWS_REGION']
NEW_SIGNUP_TOPIC = os.environ['NEW_SIGNUP_TOPIC']

logger = logging.getLogger(__name__)

class Leads(models.Model):

    def insert_lead(self, name, email, previewAccess):
        try:
            dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
            table = dynamodb.Table(STARTUP_SIGNUP_TABLE)
            table_d = dynamodb.Table('gsg-domains-table')
        except Exception as e:
            logger.error(
                'Error connecting to database table: ' + (e.fmt if hasattr(e, 'fmt') else '') + ','.join(e.args))
            return 403
        try:
            if "@" not in email:
                logger.error(
                    'Email does not contain @')
                return 422
            domain = email.split('@')[1]
            table_d.update_item(Key={'domain': domain},
                                    UpdateExpression="ADD num :val1",
                                    ExpressionAttributeValues={':val1': 1})
            response = table.put_item(
                Item={
                    'name': name,
                    'email': email,
                    'preview': previewAccess,
                },
                ReturnValues='ALL_OLD',
            )

        except Exception as e:
            logger.error(
                'Error adding item to database: ' + (e.fmt if hasattr(e, 'fmt') else '') + ','.join(e.args))
            return 403
        status = response['ResponseMetadata']['HTTPStatusCode']
        if status == 200:
            if 'Attributes' in response:
                logger.error('Existing item updated to database.')
                return 409
            logger.error('New item added to database.')
        else:
            logger.error('Unknown error inserting item to database.')

        return status

    def send_notification(self, email):
        sns = boto3.client('sns', region_name=AWS_REGION)
        try:
            sns.publish(
                TopicArn=NEW_SIGNUP_TOPIC,
                Message='New signup: %s' % email,
                Subject='New signup',
            )
            logger.error('SNS message sent.')

        except Exception as e:
            logger.error(
                'Error sending SNS message: ' + (e.fmt if hasattr(e, 'fmt') else '') + ','.join(e.args))

    def get_leads(self, domain, preview):
        try:
            dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
            table = dynamodb.Table('gsg-signup-table')
            table_d = dynamodb.Table('gsg-domains-table')
        except Exception as e:
            logger.error(
                'Error connecting to database table: ' + (e.fmt if hasattr(e, 'fmt') else '') + ','.join(e.args))
            return None
        expression_attribute_values = {}
        FilterExpression = []
        if preview:
            expression_attribute_values[':p'] = preview
            FilterExpression.append('preview = :p')
        if domain:
            expression_attribute_values[':d'] = '@' + domain
            FilterExpression.append('contains(email, :d)')
        if expression_attribute_values and FilterExpression:
            print (expression_attribute_values)
            print(FilterExpression)
            response = table.scan(
                FilterExpression=' and '.join(FilterExpression),
                ExpressionAttributeValues=expression_attribute_values,
            )
        else:
            response = table.scan(
                ReturnConsumedCapacity='TOTAL',
            )

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return response['Items']
        logger.error('Unknown error retrieving items from database.')
        return None

    def get_lead_domains(self):
        try:
            dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
            table_d = dynamodb.Table('gsg-domains-table')
        except Exception as e:
            logger.error(
                'Error connecting to database table: ' + (e.fmt if hasattr(e, 'fmt') else '') + ','.join(e.args))
            return None
        response = table_d.scan(
            ReturnConsumedCapacity='TOTAL',
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return response['Items']
        logger.error('Unknown error retrieving items from database.')
        return None

class Tweets(models.Model):

    def get_tweets(self, request):

        expression_attribute_values = {}
        FilterExpression = []

        startdate = request.GET.get("from",False)
        enddate = request.GET.get("to", False)

        if startdate:
            expression_attribute_values[':sd'] = startdate
            FilterExpression.append('created_at >= :sd')
        if enddate:
            expression_attribute_values[':ed'] = enddate
            FilterExpression.append('created_at < :ed')
        if expression_attribute_values and FilterExpression:
            print(expression_attribute_values)
            print(FilterExpression)
            response = self.table().scan(
                FilterExpression=' and '.join(FilterExpression),
                ExpressionAttributeValues=expression_attribute_values,
            )
        else:
            response = self.table().scan(
                ReturnConsumedCapacity='TOTAL',
            )

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return response['Items']
        logger.error('Unknown error retrieving items from database.')
        return None

    def table(self):
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        return dynamodb.Table('twitter-geo')



