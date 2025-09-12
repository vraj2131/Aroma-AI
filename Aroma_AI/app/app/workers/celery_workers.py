# import base64
# import json
# import logging
# import os

# import sys

# sys.path.append('../../')

# from datetime import datetime
# from datetime import timedelta
# from uuid import uuid4

# import requests
# from bs4 import BeautifulSoup
# from celery import Celery
# from geolite2 import geolite2
# import phonenumbers
# from redis import StrictRedis
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent
# from sqlalchemy import desc, and_, func, or_, case, select
# from sqlalchemy.sql import text
# from validators import url as validator_url

# from app import crud
# from app.api import deps
# from app.core.config import settings
# from app.default_initialize import DefaultInitialize
# from app.models.assistant_chat import AssistantChat, AssistantChatSources
# from app.models.assistant_chat_insights import HelpfulAnswers, NotHelpfulAnswers
# from app.models.assistant_insights import AssistantInsights
# from app.models.assistant_playground_chat import AssistantPlaygroundChat
# from app.models.assistants import Assistants, AssistantConfigurations
# from app.models.campaigns import Campaigns, CampaignTemplates, CampaignTemplateWhatsAppButtons, \
#     PendingCampaignHandler, CampaignMessageStates, CampaignInsights
# from app.models.channels import Channels, AssistantChannelsConfigurations
# from app.models.company import Companies, CompanyStatistics
# from app.models.company_insights import CompanyInsights
# from app.models.crm import CRMFields, CRMContactFields
# from app.models.document_metadata import DocumentMetadata
# from app.models.domain_extractor import DomainExtractor
# from app.models.insights import FaqInsights, NoSourcesInsights
# from app.models.languages import Languages
# from app.models.lead_assistant_insights import LeadAssistantInsights
# from app.models.lead_generation import LeadInfo, LeadInfoFields
# from app.models.sub_assistants import SubAssistantEvents
# from app.models.whatsapp_message_configuration import WhatsappHeaders, WhatsappButtonTypes, WhatsappActionTypes
# from app.vectorstore.vector_store_sklearn import VectorStoreSkLearn
# from loaders import get_loader


# class ServerDefaultInitialize:

#     def __init__(self):
#         DefaultInitialize()


# ServerDefaultInitialize()

# _logger = logging.getLogger(__name__)

# celery_app = Celery('celery_app_bg_tasks', broker=f'redis://{settings.REDIS_HOST}:6379/0')

# celery_app.conf.beat_schedule = {
#     'run_faq_insights': {
#         'task': 'celery_workers.faq_insights',
#         'schedule': timedelta(minutes=30),
#     },
#     'run_helpful_not_helpful_insights': {
#         'task': 'celery_workers.helpful_not_helpful_insights',
#         'schedule': timedelta(minutes=30),
#     },
#     'run_compute_assistant_field_values': {
#         'task': 'celery_workers.compute_assistant_field_values',
#         'schedule': timedelta(minutes=30),
#     },
#     'run_update_assistant_insights': {
#         'task': 'celery_workers.update_assistant_insights',
#         'schedule': timedelta(minutes=30),
#     },
#     'run_update_lead_assistant_insights': {
#         'task': 'celery_workers.update_lead_assistant_insights',
#         'schedule': timedelta(minutes=30),
#     },
#     'run_update_company_insights': {
#         'task': 'celery_workers.update_company_insights',
#         'schedule': timedelta(minutes=30),
#     },
#     'run_no_sources_insights': {
#         'task': 'celery_workers.no_sources_insights',
#         'schedule': timedelta(minutes=30),
#     },
#     'run_session_insights': {
#         'task': 'celery_workers.session_insights',
#         'schedule': timedelta(hours=2),
#     },
#     'run_company_statistics': {
#         'task': 'celery_workers.company_statistics',
#         'schedule': timedelta(days=1),
#     },
#     'run_assistant_configurations': {
#         'task': 'celery_workers.assistant_configurations',
#         'schedule': timedelta(days=1),
#     },
#     'run_account_expiry_action': {
#         'task': 'celery_workers.account_expiry_action',
#         'schedule': timedelta(days=1),
#     },
#     'run_daily_msg_stats_action': {
#         'task': 'celery_workers.daily_messages_stats_action',
#         'schedule': timedelta(days=1),
#     },
#     'run_check_whatsapp_template_approval': {
#         'task': 'celery_workers.check_whatsapp_template_approval',
#         'schedule': timedelta(minutes=10),
#     },
#     'run_send_campaign_messages': {
#         'task': 'celery_workers.send_campaign_messages',
#         'schedule': timedelta(minutes=10),
#     },
#     'run_update_campaign_insights': {
#         'task': 'celery_workers.update_campaign_insights',
#         'schedule': timedelta(minutes=30),
#     },
#     'run_delete_expired_campaign_document_metadata': {
#         'task': 'celery_workers.delete_expired_campaign_document_metadata',
#         'schedule': timedelta(hours=6),
#     },
#     # 'run_refresh_document_data_in_collection': {
#     #     'task': 'celery_workers.refresh_document_data_in_collection', 
#     #     'schedule': timedelta(days=1),
#     # }
# }


# @celery_app.task
# def account_expiry_action():
#     db = next(deps.get_db())
#     companies = db.query(Companies).filter(Companies.is_active == True).order_by(Companies.id.desc()).all()
#     redis_client = StrictRedis(host=settings.REDIS_HOST, port=6379, db=0, decode_responses=True)
#     sendgrid_client = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
#     for company in companies:
#         plan_details = redis_client.hgetall(f"plan_details_{company.access_token}")
#         if plan_details and plan_details.get('remaining_messages'):
#             remaining_messages = int(plan_details.get('remaining_messages'))
#             if remaining_messages <= 50:
#                 with open('mail-templates/account_action_required.html') as f:
#                     html_text = f.read()
#                     html_text = html_text.replace('{CUSTOMER_NAME}', company.company_name)
#                     html_content = HtmlContent(html_text)
#                     soup = BeautifulSoup(html_text, features="lxml")
#                     plain_text = soup.get_text()
#                     plain_text_content = Content("text/plain", plain_text)
#                 mail = Mail(Email(settings.SENDGRID_FROM_ACCOUNT), To(company.business_email),
#                             "iera - Action Required: Message Threshold Limit Reached", plain_text_content,
#                             html_content)
#                 sendgrid_client.send(message=mail)
#     return {"message": "Account Expiry CRON Successfully"}


# @celery_app.task
# def daily_messages_stats_action():
#     _logger.info("Daily Messages Stats Action Started")
#     db = next(deps.get_db())
#     current_date = datetime.now().date()
#     _logger.info("Daily Messages Stats Current Date: %s" % current_date)
#     playground_query = (
#         db.query(
#             Assistants.id.label('assistant_id'),
#             Assistants.name.label('assistant_name'),
#             Companies.id.label('company_id'),
#             Companies.company_name.label('company_name'),
#             Companies.access_token.label('company_access_token'),
#             Companies.business_email.label('business_email'),
#             func.count(AssistantPlaygroundChat.id).label('playground_message_count')
#         )
#         .outerjoin(AssistantPlaygroundChat, Assistants.id == AssistantPlaygroundChat.assistant_id)
#         .join(Companies, Companies.id == AssistantPlaygroundChat.company_id)
#         .filter(
#             func.date(AssistantPlaygroundChat.date) == current_date,
#             Companies.is_active == True,
#             Companies.is_daily_stats_send == True
#         )
#         .group_by(Assistants.id, Assistants.name, Companies.id, Companies.company_name, Companies.access_token,
#                   Companies.business_email)
#     ).subquery()
#     qna_query = (
#         db.query(
#             Assistants.id.label('assistant_id'),
#             Assistants.name.label('assistant_name'),
#             Companies.id.label('company_id'),
#             Companies.company_name.label('company_name'),
#             Companies.access_token.label('company_access_token'),
#             Companies.business_email.label('business_email'),
#             func.count(AssistantChat.id).label('qna_message_count')
#         )
#         .outerjoin(AssistantChat, Assistants.id == AssistantChat.assistant_id)
#         .join(Companies, Companies.id == AssistantChat.company_id)
#         .filter(
#             func.date(AssistantChat.date) == current_date,
#             Companies.is_active == True,
#             Companies.is_daily_stats_send == True
#         )
#         .group_by(Assistants.id, Assistants.name, Companies.id, Companies.company_name, Companies.access_token,
#                   Companies.business_email)
#     ).subquery()
#     final_query_response = (
#         db.query(
#             Assistants.id.label('assistant_id'),
#             Assistants.name.label('assistant_name'),
#             Companies.id.label('company_id'),
#             Companies.company_name.label('company_name'),
#             Companies.access_token.label('company_access_token'),
#             Companies.business_email.label('business_email'),
#             func.coalesce(playground_query.c.playground_message_count, 0).label('playground_message_count'),
#             func.coalesce(qna_query.c.qna_message_count, 0).label('qna_message_count')
#         )
#         .select_from(Assistants)
#         .outerjoin(playground_query, Assistants.id == playground_query.c.assistant_id)
#         .outerjoin(qna_query, Assistants.id == qna_query.c.assistant_id)
#         .join(Companies, (Companies.id == playground_query.c.company_id) | (Companies.id == qna_query.c.company_id))
#         .filter(
#             and_(
#                 Companies.is_active == True,
#                 Companies.is_daily_stats_send == True,
#                 or_(
#                     func.coalesce(playground_query.c.playground_message_count, 0) > 0,
#                     func.coalesce(qna_query.c.qna_message_count, 0) > 0
#                 )
#             )
#         )
#         .order_by(Assistants.id)
#     ).all()
#     _logger.info("Daily Messages Stats Current final_query_response: %r" % final_query_response)
#     if not final_query_response:
#         return {"message": "Daily Messages Stats CRON Successfully"}
#     redis_client = StrictRedis(host=settings.REDIS_HOST, port=6379, db=0, decode_responses=True)
#     sendgrid_client = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
#     for response in final_query_response:
#         plan_details = redis_client.hgetall(f"plan_details_{response[4]}")
#         _logger.info("Daily Messages Stats Current plan_details: %r" % plan_details)
#         if plan_details and plan_details.get('remaining_messages'):
#             remaining_messages = int(plan_details.get('remaining_messages'))
#             with open('mail-templates/daily_bot_usage.html') as f:
#                 html_text = f.read()
#                 html_text = html_text.replace('{ASSISTANT_NAME}', response[1])
#                 html_text = html_text.replace('{COMPANY_NAME}', response[3])
#                 html_text = html_text.replace('{DATE}', current_date.strftime('%d/%m/%Y'))
#                 html_text = html_text.replace('{CURRENT_MESSAGES_LEFT}', str(remaining_messages))
#                 html_text = html_text.replace('{TOTAL_PLAYGROUND_CHATS}', str(response[6]))
#                 html_text = html_text.replace('{TOTAL_CHANNEL_CHATS}', str(response[7]))
#                 html_content = HtmlContent(html_text)
#                 soup = BeautifulSoup(html_text, features="lxml")
#                 plain_text = soup.get_text()
#                 plain_text_content = Content("text/plain", plain_text)
#             mail = Mail(Email(settings.SENDGRID_FROM_ACCOUNT), To(response[5]),
#                         f"iera - Daily Bot Usage Report of - {response[1]} - {current_date.strftime('%d/%m/%Y')}",
#                         plain_text_content, html_content)
#             sendgrid_client.send(message=mail)
#     _logger.info("Daily Messages Stats Action Stopped")
#     return {"message": "Daily Messages Stats CRON Successfully"}


# @celery_app.task
# def faq_insights():
#     db = next(deps.get_db())
#     db.query(FaqInsights).delete()
#     subquery = db.query(
#         AssistantChat.company_id.label('company_id'),
#         AssistantChat.assistant_id.label('assistant_id'),
#         AssistantChat.question.label('question'),
#         func.count(AssistantChat.question).label('count'),
#         func.row_number().over(
#             partition_by=AssistantChat.assistant_id,
#             order_by=func.count(AssistantChat.question).desc()
#         ).label('row_num')
#     ).group_by(
#         AssistantChat.company_id,
#         AssistantChat.assistant_id,
#         AssistantChat.question
#     ).subquery()
#     faq_table = db.query(subquery.c.company_id, subquery.c.assistant_id, subquery.c.question, subquery.c.count). \
#         filter(subquery.c.row_num <= 100). \
#         order_by(subquery.c.assistant_id, subquery.c.count.desc()).all()
#     objects = [
#         FaqInsights(company_id=row.company_id, assistant_id=row.assistant_id, question=row.question, count=row.count)
#         for row in faq_table]
#     db.add_all(objects)
#     db.commit()
#     db.close()
#     return {"message": "FAQ Computed Successfully"}


# def helpful_groupby_answer(db, category):
#     subquery = db.query(
#         AssistantChat.company_id.label('company_id'),
#         AssistantChat.question.label('question'),
#         AssistantChat.assistant_id.label('assistant_id'),
#         AssistantChat.answer.label('answer'),
#         func.row_number().over(
#             partition_by=AssistantChat.assistant_id,
#             order_by=AssistantChat.date.desc()
#         ).label('row_num')
#     ).where(
#         AssistantChat.is_helpful == category
#     ).group_by(
#         AssistantChat.company_id,
#         AssistantChat.question,
#         AssistantChat.assistant_id,
#         AssistantChat.answer,
#         AssistantChat.date,
#         AssistantChat.is_helpful
#     ).order_by(
#         AssistantChat.date.desc()
#     ).subquery()
#     return db.query(
#         subquery.c.company_id,
#         subquery.c.assistant_id,
#         subquery.c.question,
#         subquery.c.answer
#     ).distinct(subquery.c.answer).where(subquery.c.row_num <= 100)


# @celery_app.task
# def helpful_not_helpful_insights():
#     db = next(deps.get_db())
#     db.query(HelpfulAnswers).delete()
#     db.add_all([HelpfulAnswers(company_id=row.company_id, assistant_id=row.assistant_id, question=row.question,
#                                answer=row.answer) for row in helpful_groupby_answer(db, 1)])
#     db.commit()
#     db.query(NotHelpfulAnswers).delete()
#     db.add_all([NotHelpfulAnswers(company_id=row.company_id, assistant_id=row.assistant_id, question=row.question,
#                                   answer=row.answer) for row in helpful_groupby_answer(db, -1)])
#     db.commit()
#     db.close()
#     return {"message": "Helpful / Not Helpful Computed Successfully"}


# @celery_app.task(autoretry_for=(Exception,), retry_backoff=3)
# def manage_qna_sessions(*args, **kwargs):
#     if not args and not args[0]:
#         return {"message": "Arguments not provided"}
#     db = next(deps.get_db())
#     _logger.info("Manage QNA session args[0] : %s" % args[0])
#     assistant_chat_id = db.query(AssistantChat).filter(AssistantChat.id == args[0]).first()
#     if not assistant_chat_id:
#         return {"message": f"Assistant Chat Record not Found for chat id {args[0]}"}
#     _logger.info("Manage QNA session assistant_chat_id : %s" % assistant_chat_id.id)
#     redis_client = StrictRedis(host=settings.REDIS_HOST, port=6379, db=0)
#     current_time = datetime.now()
#     last_time = redis_client.hget(f"qna_session_{assistant_chat_id.user_id}", 'last_interaction')
#     _logger.info("Manage QNA session getting last interaction value : %s" % last_time)
#     time_difference = 0
#     if last_time:
#         last_time = last_time.decode()
#         last_time = datetime.strptime(last_time, '%d-%m-%Y %H:%M:%S')
#         time_difference = current_time - last_time
#     current_time = current_time.strftime("%d-%m-%Y %H:%M:%S")
#     if not last_time or (time_difference >= timedelta(minutes=30)):
#         session = f"{uuid4()}_{assistant_chat_id.user_id}"
#         _logger.info("Manage QNA session in if session : %s" % session)
#         redis_client.hset(f"qna_session_{assistant_chat_id.user_id}", 'last_session', session)
#         assistant_chat_id.session = session
#         db.commit()
#         db.refresh(assistant_chat_id)
#     else:
#         _logger.info("Manage QNA session in else")
#         assistant_chat_id.session = redis_client.hget(f"qna_session_{assistant_chat_id.user_id}",
#                                                       'last_session').decode()
#         db.commit()
#     redis_client.hset(f"qna_session_{assistant_chat_id.user_id}", 'last_interaction', current_time)
#     _logger.info("Manage QNA session updating last interaction value")
#     msg_id = assistant_chat_id.id
#     db.close()
#     return {"message": f"Session Stored Computed Successfully for chat id {msg_id}"}


# @celery_app.task(autoretry_for=(Exception,), retry_backoff=3)
# def compute_qna_regions(*args, **kwargs):
#     if not args and not args[0] and not args[1]:
#         return {"message": "Arguments not provided"}
#     db = next(deps.get_db())
#     _logger.info("Compute QNA Regions args[0] : %s" % args[0])
#     assistant_chat_id = db.query(AssistantChat).filter(AssistantChat.id == args[0]).first()
#     if not assistant_chat_id:
#         return {"message": f"Assistant Chat Record not Found for chat id {args[0]}"}
#     _logger.info("Compute QNA Regions assistant_chat_id : %s" % assistant_chat_id.id)
#     msg_id = assistant_chat_id.id
#     try:
#         reader = geolite2.reader()
#         geo_details = reader.get(args[1])
#         if geo_details:
#             assistant_chat_id.city = geo_details.get('city', {}).get('names', {}).get('en')
#             assistant_chat_id.country = geo_details.get('country', {}).get('names', {}).get('en')
#             assistant_chat_id.latitude = geo_details.get('location', {}).get('latitude')
#             assistant_chat_id.longitude = geo_details.get('location', {}).get('longitude')
#             db.commit()
#             db.close()
#             _logger.info("Compute QNA Regions Computed")
#     except Exception as e:
#         db.close()
#         _logger.error("Compute QNA Regions Exception : %s" % e)
#         return {"message": f"Error while Computing Regions {e} for chat id {msg_id}"}
#     return {"message": f"QnA Regions Computed Successfully for chat id {msg_id}"}


# @celery_app.task(autoretry_for=(Exception,), retry_backoff=3)
# def compute_lead_generation_regions(*args, **kwargs):
#     if not args and not args[0] and not args[1]:
#         return {"message": "Arguments not provided"}
#     db = next(deps.get_db())
#     _logger.info("Compute Lead Generation Regions args[0] : %s" % args[0])
#     lead_id = db.query(LeadInfo).filter(LeadInfo.lead_id == args[0]).first()
#     if not lead_id:
#         return {"message": f"Lead Record not Found for id {args[0]}"}
#     _logger.info("Compute Lead Generation Regions lead_id : %s" % args[0])
#     try:
#         reader = geolite2.reader()
#         geo_details = reader.get(args[1])
#         if geo_details:
#             lead_id.city = geo_details.get('city', {}).get('names', {}).get('en')
#             lead_id.country = geo_details.get('country', {}).get('names', {}).get('en')
#             lead_id.latitude = geo_details.get('location', {}).get('latitude')
#             lead_id.longitude = geo_details.get('location', {}).get('longitude')
#             db.commit()
#             db.close()
#             _logger.info("Compute Lead Genertion Regions Computed")
#     except Exception as e:
#         db.close()
#         _logger.error("Compute Lead Genertion Regions Exception : %s" % e)
#         return {"message": f"Error while Computing Regions {e} for lead id {args[0]}"}
#     return {"message": f"Lead Generation Regions Computed Successfully for lead id {args[0]}"}


# @celery_app.task
# def compute_assistant_field_values():
#     db = next(deps.get_db())
#     db.execute(text("""UPDATE assistants ast SET compute_total_conversations =
#     (SELECT COUNT(ac.question) FROM assistant_chat ac WHERE ac.assistant_id = ast.id
#     AND ac.company_id = ast.company_id) WHERE ast.function = 'Web Assistant';"""))
#     db.commit()
#     db.execute(text("""UPDATE assistants ast SET compute_total_users =
#     (SELECT COUNT(DISTINCT(ac.user_id)) FROM assistant_chat ac WHERE ac.assistant_id = ast.id
#     AND ac.company_id = ast.company_id) WHERE ast.function = 'Web Assistant';"""))
#     db.commit()
#     db.execute(text("""UPDATE assistants ast
#     SET compute_total_leads = (SELECT COUNT(DISTINCT li.lead_id) FROM lead_info li
#     WHERE (li.assistant_id = ast.id OR li.assistant_id IN (SELECT sub.id
#     FROM assistants sub WHERE sub.sub_assistant_id = ast.id))
#     AND li.lead_state = 'new')
#     WHERE ast.function = 'Lead Generation';"""))
#     db.commit()
#     db.execute(text(f"""UPDATE assistants ast
#     SET compute_total_qualified_leads = (SELECT COUNT(DISTINCT li.lead_id) FROM lead_info li
#     WHERE (li.assistant_id = ast.id OR li.assistant_id IN (SELECT sub.id
#     FROM assistants sub WHERE sub.sub_assistant_id = ast.id))
#     AND li.lead_quality > {settings.QUALIFIED_LEAD_THRESHOLD}
#     AND li.lead_state = 'new')
#     WHERE ast.function = 'Lead Generation';"""))
#     db.commit()
#     return {"message": "Assistant Computed Successfully"}


# @celery_app.task(autoretry_for=(Exception,), retry_backoff=3)
# def compute_chat_sources(*args, **kwargs):
#     if not args and not args[0]:
#         return {"message": "Arguments not provided"}
#     db = next(deps.get_db())
#     _logger.info("Compute Chat Sources args[0] : %s" % args[0])
#     assistant_chat_id = db.query(AssistantChat).filter(AssistantChat.id == args[0]).first()
#     if not assistant_chat_id:
#         return {"message": f"Assistant Chat Record not Found for chat id {args[0]}"}
#     _logger.info("Compute Chat Sources assistant_chat_id : %s" % assistant_chat_id.id)
#     is_source = False
#     if args[1]:
#         for source in args[1]:
#             source = source.strip()
#             if not source or source == "N/A":
#                 source_type = ''
#                 is_source = False
#             elif validator_url(source):
#                 source_type = "website"
#                 is_source = True
#             else:
#                 source_type = os.path.splitext(source)[-1]
#                 is_source = True
#             db.add(AssistantChatSources(company_id=assistant_chat_id.company_id,
#                                         assistant_id=assistant_chat_id.assistant_id,
#                                         assistant_chat_id=assistant_chat_id.id,
#                                         source_type=source_type,
#                                         is_source_found=is_source,
#                                         sources=source))
#             db.commit()
#         assistant_chat_id.is_source_found = True
#         db.commit()
#         _logger.info("Compute Chat Sources Found")
#     else:
#         source_type = ''
#         source = ''
#         db.add(AssistantChatSources(company_id=assistant_chat_id.company_id,
#                                     assistant_id=assistant_chat_id.assistant_id,
#                                     assistant_chat_id=assistant_chat_id.id,
#                                     source_type=source_type,
#                                     is_source_found=is_source,
#                                     sources=source))
#         db.commit()
#         assistant_chat_id.is_source_found = is_source
#         db.commit()
#         _logger.info("Compute Chat No Sources Found")
#     msg_id = assistant_chat_id.id
#     db.close()
#     return {"message": f"Chat Sources Computed Successfully for chat id {msg_id}"}


# @celery_app.task(autoretry_for=(Exception,), retry_backoff=3)
# def train_document(*args, **kwargs):
#     if not args and not args[0]:
#         return {"message": "Arguments not provided"}
#     db = next(deps.get_db())
#     _logger.info("Train Document args[0] : %s" % args[0])
#     document_id = db.query(DocumentMetadata).filter(DocumentMetadata.id == args[0]).first()
#     if not document_id:
#         return {"message": f"Document Record not Found for document id {args[0]}"}
#     _logger.info("Train Document document_id : %s" % document_id.id)
#     if document_id.type in ['Video', 'Website Crawler', 'Website Page']:
#         loader = get_loader(document_id.path)
#     elif document_id.type == "google_drive":
#         company_id = db.query(Companies).filter(Companies.id == document_id.company_id).first()
#         assistant_id = db.query(Assistants).filter(Assistants.id == document_id.assistant_id).first()
#         loader = get_loader(document_id.path, document_id.type, company_id, assistant_id)
#     else:
#         loader = get_loader(f"{os.getcwd()}/../{document_id.path}")
#     # TODO: Need to add dynamic configuration reading and calling methods
#     docs_response = loader.extract_docs(20, 2)
#     msg_id = document_id.id
#     if not docs_response.get('success'):
#         document_id.status = 'failed'
#         document_id.failed_reason = docs_response.get('message')
#         db.commit()
#         db.close()
#         _logger.info("Train Document Failed due to : %s" % docs_response.get('message'))
#         return {"message": f"Unable to Train the Document due to some Error for document id {msg_id}"}
#     vector_store = VectorStoreSkLearn(
#         f"{os.getcwd()}/../{settings.SKLEARN_DB_PATH}/{document_id.company_id}/{document_id.assistant_id}",
#         DefaultInitialize._instance_['embeddings'])
#     is_done = vector_store.store_docs_to_collection(docs_response.get('pages'), document_id.id, document_id.path)
#     if is_done:
#         _logger.info("Train Document Trained")
#         document_id.status = 'done'
#         db.commit()
#     db.close()
#     return {"message": f"Document Trained Successfully for document id {msg_id}"}


# @celery_app.task(autoretry_for=(Exception,), retry_backoff=3)
# def delete_website_crawler_document(*args, **kwargs):
#     if not args and not args[0]:
#         return {"message": "Arguments not provided"}
#     db = next(deps.get_db())
#     _logger.info("Delete Website Crawler Document args[0] : %s" % args[0])
#     domain_extractor_id = db.query(DomainExtractor).filter(DomainExtractor.id == args[0]).first()
#     if not domain_extractor_id:
#         return {"message": f"Document Extractor Record not Found for domain extractor id {args[0]}"}
#     _logger.info("Delete Website Crawler domain_extractor_id : %s" % domain_extractor_id.id)
#     document_ids = db.query(DocumentMetadata).filter(DocumentMetadata.domain_extractor_id == domain_extractor_id.id,
#                                                      DocumentMetadata.company_id == domain_extractor_id.company_id,
#                                                      DocumentMetadata.assistant_id == domain_extractor_id.assistant_id,
#                                                      DocumentMetadata.type == 'Website Crawler').all()
#     if document_ids:
#         for document in document_ids:
#             vector_path = f"{os.getcwd()}/../{settings.SKLEARN_DB_PATH}/{domain_extractor_id.company_id}/{domain_extractor_id.assistant_id}"
#             res, _ = crud.document.delete_document_vector_celery_worker(vector_path, document.id)
#             if res:
#                 db.query(DocumentMetadata).filter(DocumentMetadata.id == document.id,
#                                                   DocumentMetadata.company_id == domain_extractor_id.company_id,
#                                                   DocumentMetadata.assistant_id == domain_extractor_id.assistant_id,
#                                                   DocumentMetadata.type == 'Website Crawler').delete()
#                 db.commit()
#     db.query(DomainExtractor).filter(DomainExtractor.id == domain_extractor_id.id).delete()
#     db.commit()
#     msg_id = domain_extractor_id.id
#     db.close()
#     return {"message": f"Website Crawler Deleted Successfully for document id {msg_id}"}


# @celery_app.task
# def update_assistant_insights():
#     db = next(deps.get_db())
#     current_datetime = datetime.now()
#     current_datetime_formatted = current_datetime.strftime('%Y-%m-%d')
#     assistant_ids = db.query(Assistants).order_by(Assistants.id.asc()).all()
#     for assistant in assistant_ids:
#         if not db.query(AssistantInsights).filter(AssistantInsights.company_id == assistant.company_id,
#                                                   AssistantInsights.assistant_id == assistant.id,
#                                                   AssistantInsights.date == current_datetime_formatted).first():
#             insight_id = AssistantInsights(**{'company_id': assistant.company_id, 'assistant_id': assistant.id,
#                                               'date': current_datetime_formatted, 'helpful_answers': 0,
#                                               'not_helpful_answers': 0, 'dint_answers': 0, 'users': 0,
#                                               'sessions': 0, 'queries_session': 0, 'queries_user': 0, 'queries': 0,
#                                               'sources_found': 0, 'sources_not_found': 0, 'knowledge_base': 0})
#             db.add(insight_id)
#             db.commit()
#             db.refresh(insight_id)
#     db.execute(text(f"""UPDATE assistant_insights ai
#         SET helpful_answers = sub.helpful_answers, not_helpful_answers = sub.not_helpful_answers,
#         dint_answers = sub.dint_answers, users = sub.users, sessions = sub.sessions,
#         queries_session = sub.queries_session, queries_user = sub.queries_user, queries = sub.queries,
#         sources_found = sub.sources_found, sources_not_found = sub.sources_not_found
#         FROM ( SELECT company_id, assistant_id, TO_DATE(TO_CHAR(date, 'YYYYMMDD'), 'YYYYMMDD') AS date,
#         COUNT(is_helpful) FILTER(WHERE is_helpful = 1) AS helpful_answers,
#         COUNT(is_helpful) FILTER(WHERE is_helpful = -1) AS not_helpful_answers,
#         COUNT(is_helpful) FILTER(WHERE is_helpful = 0) AS dint_answers,
#         COUNT(DISTINCT(user_id)) AS users, COUNT(DISTINCT(session)) AS sessions,
#         (COALESCE(COUNT(question), 1) / COALESCE(NULLIF(COUNT(DISTINCT session), 0), 1)) AS queries_session,
#         (COALESCE(COUNT(question), 1) / COALESCE(NULLIF(COUNT(DISTINCT user_id), 0), 1)) AS queries_user,
#         COUNT(question) AS queries, COUNT(is_source_found) FILTER(WHERE is_source_found = 't') AS sources_found,
#         COUNT(is_source_found) FILTER(WHERE is_source_found = 'f') AS sources_not_found
#         FROM assistant_chat
#         WHERE TO_CHAR(date, 'YYYYMMDD') = '{current_datetime.strftime('%Y%m%d')}'
#         GROUP BY company_id, assistant_id, TO_CHAR(date, 'YYYYMMDD')) sub
#         WHERE ai.company_id = sub.company_id AND ai.assistant_id = sub.assistant_id AND ai.date = sub.date;
#     """))
#     db.commit()
#     db.execute(text(f"""UPDATE assistant_insights ai SET knowledge_base = subquery.no_of_documents
#         FROM (SELECT COUNT(id) no_of_documents, assistant_id, company_id FROM document_metadata
#         WHERE TO_CHAR(date, 'YYYYMMDD') = \'{current_datetime.strftime('%Y%m%d')}\'
#         GROUP BY assistant_id, company_id) AS subquery
#         WHERE TO_CHAR(ai.date, 'YYYYMMDD') = \'{current_datetime.strftime('%Y%m%d')}\'
#         AND ai.assistant_id = subquery.assistant_id AND ai.company_id = subquery.company_id;
#     """))
#     db.commit()
#     db.close()
#     return {"message": "Assistant Insights Computed Successfully"}


# @celery_app.task(autoretry_for=(Exception,), retry_backoff=3)
# def update_duplicate_lead(*args, **kwargs):
#     if not args and not args[0]:
#         return {"message": "Arguments not provided"}
#     lead_info_id = args[0]
#     db = next(deps.get_db())
#     subquery = (
#         db.query(LeadInfoFields.field_key, LeadInfoFields.field_value)
#         .filter(LeadInfoFields.lead_info_id == lead_info_id)
#     ).subquery()
#     duplicate_lead_ids = (
#         db.query(LeadInfoFields.lead_info_id)
#         .filter(
#             or_(
#                 and_(
#                     LeadInfoFields.field_key == 'email',
#                     LeadInfoFields.field_value == subquery.c.field_value
#                 ),
#                 and_(
#                     LeadInfoFields.field_key == 'phone',
#                     LeadInfoFields.field_value == subquery.c.field_value
#                 )
#             )
#         )
#         .distinct()
#         .all()
#     )
#     duplicate_lead_ids = [entry[0] for entry in duplicate_lead_ids]
#     if duplicate_lead_ids:
#         db.query(LeadInfo).filter(LeadInfo.id.in_(duplicate_lead_ids)).update(
#             {"is_duplicate": True}, synchronize_session=False
#         )
#         db.commit()
#     return {"message": "Duplicate Leads Updated Successfully"}


# def get_upload_header(whatsapp_access_token, file_dict):
#     if not file_dict:
#         return False
#     get_session_url = f"{settings.WHATSAPP_BASE_URL}/{settings.IERA_WHATSAPP_BUSINESS_API_ID}/uploads?file_name={file_dict.get('file_name', '')}&file_length={file_dict.get('file_size', '')}&file_type={file_dict.get('mime_type', '')}&access_token={whatsapp_access_token}"
#     response = requests.post(get_session_url)
#     if response.status_code != 200:
#         return False
#     response_data = response.json()
#     if not response_data.get("id", False):
#         return False
#     session_id = response_data.get("id")
#     if not session_id:
#         return False
#     get_header_url = f"{settings.WHATSAPP_BASE_URL}/{session_id}"
#     headers = {
#         "Authorization": f"OAuth {whatsapp_access_token}",
#         "file_offset": "0"
#     }
#     file_data = base64.b64decode(file_dict.get('file_data', ''))
#     header_handle_response = requests.post(get_header_url, headers=headers, data=file_data)
#     if not header_handle_response.status_code == 200:
#         return False
#     header_handle_response_data = header_handle_response.json()
#     if not header_handle_response_data.get("h", False):
#         return False
#     header_handle_id = header_handle_response_data.get("h")
#     return header_handle_id


# @celery_app.task(autoretry_for=(Exception,), retry_backoff=3)
# def send_campaign_template_for_approval(*args, **kwargs):
#     db = next(deps.get_db())
#     campaign_template_id = db.query(CampaignTemplates).filter(CampaignTemplates.id == args[0]).first()
#     if not campaign_template_id:
#         return {"message": f"Campaign Template not found for id {args[0]}"}
#     try:
#         language_id = db.query(Languages).filter(Languages.id == campaign_template_id.language_id).first()
#         if not language_id:
#             return {"message": "Language not found"}
#         channel_id = db.query(Channels).filter(Channels.key == "whatsapp").first()
#         if not channel_id:
#             return {"message": "Channel not found"}
#         channel_configuration_id = db.query(AssistantChannelsConfigurations).filter(
#             AssistantChannelsConfigurations.company_id == campaign_template_id.company_id,
#             AssistantChannelsConfigurations.channel_id == channel_id.id,
#             AssistantChannelsConfigurations.assistant_id == campaign_template_id.assistant_id
#         ).first()
#         if not channel_configuration_id:
#             return {"message": "Channel Configuration not found"}
#         whatsapp_config = channel_configuration_id.configurations
#         WHATSAPP_BUSINESS_ID = whatsapp_config.get('whatsapp_waba_id')
#         WHATSAPP_TOKEN = whatsapp_config.get('whatsapp_token')
#         if campaign_template_id:
#             url = f"{settings.WHATSAPP_BASE_URL}/{WHATSAPP_BUSINESS_ID}/message_templates"
#             headers = {
#                 "Authorization": f"Bearer {WHATSAPP_TOKEN}",
#                 "Content-Type": "application/json"
#             }
#             components = []
#             whatsapp_header_id = db.query(WhatsappHeaders).filter(
#                 WhatsappHeaders.id == campaign_template_id.whatsapp_header_id
#             ).first()
#             if whatsapp_header_id and whatsapp_header_id.key != "none":
#                 header_component = {"type": "HEADER", "format": whatsapp_header_id.key.upper()}
#                 if whatsapp_header_id.key == "text":
#                     header_component["text"] = campaign_template_id.whatsapp_formatted_header_value
#                     header_variables = list(filter(lambda x: x.variable_type.lower() == "header",
#                                                    campaign_template_id.whatsapp_variable_ids))
#                     header_variables = [header.sample_value for header in header_variables]
#                     if header_variables:
#                         header_component["example"] = {
#                             "header_text": [
#                                 header_variables
#                             ]
#                         }
#                 elif whatsapp_header_id.key in ["image", "video", "document"]:
#                     redis_client = StrictRedis(host=settings.REDIS_HOST, port=6379, db=0, decode_responses=True)
#                     key = args[1]
#                     if not key:
#                         return {"message": "File not found"}
#                     file_dict = redis_client.get(key)
#                     file_dict = json.loads(file_dict)
#                     header_handle = get_upload_header(WHATSAPP_TOKEN, file_dict)
#                     redis_client.delete(key)
#                     if not header_handle:
#                         return {"message": "Error in uploading file"}
#                     header_component["example"] = {"header_handle": [header_handle]}
#                     db.commit()
#                     db.refresh(campaign_template_id)
#                 components.append(header_component)

#             body_variables = list(
#                 filter(lambda x: x.variable_type.lower() == "body", campaign_template_id.whatsapp_variable_ids))
#             body_variables = [body.sample_value for body in body_variables]
#             body_component = {
#                 "type": "BODY",
#                 "text": campaign_template_id.whatsapp_formatted_body
#             }
#             if body_variables:
#                 body_component["example"] = {
#                     "body_text": [
#                         body_variables
#                     ]
#                 }

#             components.append(body_component)

#             if campaign_template_id.whatsapp_footer:
#                 components.append({
#                     "type": "FOOTER",
#                     "text": campaign_template_id.whatsapp_footer
#                 })
#             if campaign_template_id.whatsapp_button_ids:
#                 whatsapp_button_ids_list = [button.id for button in campaign_template_id.whatsapp_button_ids]
#                 whatsapp_button_ids = db.query(CampaignTemplateWhatsAppButtons).filter(
#                     CampaignTemplateWhatsAppButtons.id.in_(whatsapp_button_ids_list)
#                 ).all()
#                 button_components = []
#                 for button_id in whatsapp_button_ids:
#                     whatsapp_button_id = db.query(WhatsappButtonTypes).filter(
#                         WhatsappButtonTypes.id == button_id.whatsapp_button_type_id
#                     ).first()
#                     if whatsapp_button_id.key == "QUICK_REPLY":
#                         button_components.append({
#                             "type": "QUICK_REPLY",
#                             "text": button_id.whatsapp_button_text
#                         })
#                     elif whatsapp_button_id.key == "CALL_TO_ACTION":
#                         whatsapp_action_id = db.query(WhatsappActionTypes).filter(
#                             WhatsappActionTypes.id == button_id.whatsapp_action_type_id
#                         ).first()
#                         if whatsapp_action_id.key == "URL":
#                             button_components.append({
#                                 "type": "URL",
#                                 "text": button_id.whatsapp_button_text,
#                                 "url": button_id.whatsapp_button_value,
#                             })
#                         elif whatsapp_action_id.key == "PHONE_NUMBER":
#                             button_components.append({
#                                 "type": "PHONE_NUMBER",
#                                 "text": button_id.whatsapp_button_text,
#                                 "phone_number": button_id.whatsapp_button_value,
#                             })
#                 components.append({
#                     "type": "BUTTONS",
#                     "buttons": button_components
#                 })
#             payload = {
#                 "name": campaign_template_id.name,
#                 "language": language_id.key,
#                 "components": components,
#                 "category": "MARKETING"
#             }
#             response = requests.post(url, headers=headers, json=payload)
#             if response.status_code == 200:
#                 response_data = response.json()
#                 template_id = response_data.get("id")
#                 campaign_template_id.whatsapp_template_id = template_id
#                 campaign_template_id.status = 'Requested'
#                 campaign_template_id.write_date = datetime.now()
#                 db.commit()
#                 db.refresh(campaign_template_id)
#                 db.close()
#                 quick_check_campaign_template_approval.apply_async(args=[campaign_template_id.id], countdown=30)
#                 return {"message": "Template sent for approval successfully"}
#             else:
#                 campaign_template_id.status = 'Failed'
#                 campaign_template_id.write_date = datetime.now()
#                 db.commit()
#                 db.refresh(campaign_template_id)
#                 db.close()
#                 return {"message": f"Error: {response.status_code} {response.text}"}
#     except Exception as e:
#         campaign_template_id.status = 'Failed'
#         campaign_template_id.write_date = datetime.now()
#         db.commit()
#         db.refresh(campaign_template_id)
#         db.close()
#         return {"message": f"Error: {e}"}


# def send_campaign_template_approval_request(db, campaign_template_id, whatsapp_config):
#     if not campaign_template_id.whatsapp_template_id:
#         campaign_template_id.status = 'Failed'
#         db.commit()
#         db.refresh(campaign_template_id)
#     url = f"{settings.WHATSAPP_BASE_URL}/{campaign_template_id.whatsapp_template_id}"
#     headers = {
#         "Authorization": f"Bearer {whatsapp_config.get('whatsapp_token')}",
#         "Content-Type": "application/json"
#     }
#     response = requests.get(url, headers=headers)
#     if response.status_code == 200:
#         status = response.json().get('status')
#         if status == 'APPROVED':
#             campaign_template_id.status = 'Approved'
#         elif status == 'REJECTED':
#             campaign_template_id.status = 'Rejected'
#         campaign_template_id.write_date = datetime.now()
#         db.commit()
#         db.refresh(campaign_template_id)
#     return True


# @celery_app.task(autoretry_for=(Exception,), retry_backoff=3)
# def quick_check_campaign_template_approval(campaign_template):
#     db = next(deps.get_db())
#     campaign_template_id = db.query(CampaignTemplates).filter(CampaignTemplates.id == campaign_template).first()
#     if not campaign_template_id:
#         return {"message": f"Campaign Template not found for id {campaign_template_id}"}
#     channel_id = db.query(Channels).filter(Channels.key == "whatsapp").first()
#     if not channel_id:
#         return {"message": "Channel not found"}
#     channel_configuration_id = db.query(AssistantChannelsConfigurations).filter(
#         AssistantChannelsConfigurations.company_id == campaign_template_id.company_id,
#         AssistantChannelsConfigurations.channel_id == channel_id.id,
#         AssistantChannelsConfigurations.assistant_id == campaign_template_id.assistant_id
#     ).first()
#     if not channel_configuration_id:
#         return {"message": "Channel configuration not found"}
#     whatsapp_config = channel_configuration_id.configurations
#     send_campaign_template_approval_request(db, campaign_template_id, whatsapp_config)
#     db.close()
#     return {"message": "Quick Check Whatsapp Template Approval Successfully"}


# @celery_app.task
# def check_whatsapp_template_approval():
#     db = next(deps.get_db())
#     campaign_template_ids = db.query(CampaignTemplates).filter(CampaignTemplates.status == 'Requested').all()
#     if not campaign_template_ids:
#         return {"message": "Campaign Templates not found"}
#     channel_id = db.query(Channels).filter(Channels.key == "whatsapp").first()
#     if not channel_id:
#         return {"message": "Channel not found"}
#     whatsapp_config_dict = {}
#     assistant_ids = db.query(Assistants).filter(Assistants.function == 'Web Assistant').all()
#     for assistant_id in assistant_ids:
#         channel_configuration_id = db.query(AssistantChannelsConfigurations).filter(
#             AssistantChannelsConfigurations.company_id == assistant_id.company_id,
#             AssistantChannelsConfigurations.channel_id == channel_id.id,
#             AssistantChannelsConfigurations.assistant_id == assistant_id.id
#         ).first()
#         if not channel_configuration_id:
#             continue
#         whatsapp_config = channel_configuration_id.configurations
#         whatsapp_config_dict[assistant_id.id] = {
#             'WHATSAPP_BUSINESS_ID': whatsapp_config.get('whatsapp_waba_id', False),
#             'whatsapp_token': whatsapp_config.get('whatsapp_token', False)
#         }
#     for campaign_template_id in campaign_template_ids:
#         whatsapp_config = whatsapp_config_dict.get(campaign_template_id.assistant_id, False)
#         if not whatsapp_config:
#             continue
#         send_campaign_template_approval_request(db, campaign_template_id, whatsapp_config)
#     db.close()
#     return {"message": "Check Whatsapp Template Approval Successfully"}


# @celery_app.task
# def send_campaign_messages():
#     db = next(deps.get_db())
#     total_limit = 50
#     retry_campaigns = db.query(PendingCampaignHandler).filter(
#         PendingCampaignHandler.is_retry == True,
#         PendingCampaignHandler.state == 'retry',
#         PendingCampaignHandler.next_execution <= datetime.now(),
#     ).order_by(PendingCampaignHandler.id.asc()).limit(total_limit).all()
#     total_limit -= len(retry_campaigns)
#     instant_limit = int(total_limit * 0.7)
#     scheduled_limit = total_limit - instant_limit
#     instant_campaigns = db.query(PendingCampaignHandler).filter(
#         PendingCampaignHandler.state == 'pending',
#         PendingCampaignHandler.scheduled_date <= datetime.now(),
#         PendingCampaignHandler.type == 'instant'
#     ).order_by(PendingCampaignHandler.id.asc()).limit(instant_limit).all()
#     if len(instant_campaigns) < instant_limit:
#         scheduled_limit = total_limit - len(instant_campaigns)
#     scheduled_campaigns = db.query(PendingCampaignHandler).filter(
#         PendingCampaignHandler.state == 'pending',
#         PendingCampaignHandler.scheduled_date <= datetime.now(),
#         PendingCampaignHandler.type == 'scheduled'
#     ).order_by(PendingCampaignHandler.id.asc()).limit(scheduled_limit).all()
#     pending_campaigns = retry_campaigns + instant_campaigns + scheduled_campaigns
#     campaign_list = []
#     if not pending_campaigns:
#         return {"message": "No pending campaign phone numbers"}
#     template_dict = {}
#     distinct_template_ids = list(set(pending_campaign.template_id for pending_campaign in pending_campaigns))
#     campaign_templates = db.query(CampaignTemplates).filter(CampaignTemplates.id.in_(distinct_template_ids)).all()
#     template_dict = {template.id: template for template in campaign_templates}
#     redis_client = StrictRedis(host=settings.REDIS_HOST, port=6379, db=0, decode_responses=True)
#     for pending_campaign in pending_campaigns:
#         contact_number = f'+{pending_campaign.contact_number}' if '+' not in pending_campaign.contact_number else pending_campaign.contact_number
#         phone_number = phonenumbers.parse(contact_number, None)
#         if not phonenumbers.is_valid_number(phone_number):
#             pending_campaign.state = "failed"
#             message = "Could not send the message due to invalid contact number"
#             db.commit()
#             db.refresh(pending_campaign)
#             campaign_message_state = CampaignMessageStates(
#                 pending_campaign_handler_id=pending_campaign.id,
#                 state=pending_campaign.state,
#                 message=message
#             )
#             db.add(campaign_message_state)
#             db.commit()
#             continue
#         key = f"campaign_template:{pending_campaign.company_id}:{pending_campaign.assistant_id}:{pending_campaign.template_id}:{pending_campaign.campaign_id}"
#         whatsapp_dict = redis_client.get(key)
#         if not whatsapp_dict:
#             continue
#         whatsapp_dict = json.loads(whatsapp_dict)
#         template_json = whatsapp_dict.get('template_json', False)
#         if template_json:
#             whatsapp_config = whatsapp_dict.get('whatsapp_config_dict')
#             url = f"{settings.WHATSAPP_BASE_URL}/{whatsapp_config.get('WHATSAPP_PHONE_NUMBER_ID')}/messages"
#             headers = {
#                 "Authorization": f"Bearer {whatsapp_config.get('WHATSAPP_TOKEN')}",
#                 "Content-Type": "application/json"
#             }
#             template_id = template_dict.get(pending_campaign.template_id, False)
#             header_variables = list(
#                 filter(lambda x: x.variable_type.lower() == "header", template_id.whatsapp_variable_ids))
#             if header_variables:
#                 field_id = db.query(CRMFields).filter(
#                     CRMFields.id == header_variables[0].field_id).first()
#                 crm_contact_field_id = db.query(CRMContactFields).filter(
#                     CRMContactFields.crm_contact_id == pending_campaign.crm_contact_id,
#                     CRMContactFields.field_name == field_id.field_name).first()
#                 if crm_contact_field_id:
#                     if "components" not in template_json:
#                         template_json['components'] = []
#                     template_json['components'].append(
#                         {
#                             "type": "header",
#                             "parameters": [
#                                 {
#                                     "type": "text",
#                                     "text": crm_contact_field_id.field_value
#                                 }
#                             ]
#                         }
#                     )
#             body_variables = list(
#                 filter(lambda x: x.variable_type.lower() == "body", template_id.whatsapp_variable_ids))
#             if body_variables:
#                 if "components" not in template_json:
#                     template_json['components'] = []
#                 body_dict = {
#                     "type": "body",
#                     "parameters": []
#                 }
#                 for variable in body_variables:
#                     field_id = db.query(CRMFields).filter(
#                         CRMFields.id == variable.field_id).first()
#                     crm_contact_field_id = db.query(CRMContactFields).filter(
#                         CRMContactFields.crm_contact_id == pending_campaign.crm_contact_id,
#                         CRMContactFields.field_name == field_id.field_name).first()
#                     if crm_contact_field_id:
#                         body_dict["parameters"].append({
#                             "type": "text",
#                             "text": crm_contact_field_id.field_value
#                         })
#                 template_json['components'].append(body_dict)
#             payload = {
#                 "messaging_product": "whatsapp",
#                 "recipient_type": "individual",
#                 "to": pending_campaign.contact_number,
#                 "type": "template",
#                 "template": template_json,
#                 "biz_opaque_callback_data": "iera-campaign-message"
#             }
#             campaign_list.append(pending_campaign.campaign_id)
#             message = ""
#             response = requests.post(url, headers=headers, json=payload)
#             if response.status_code == 200:
#                 message_data = response.json()
#                 message_id = message_data['messages'][0]['id']
#                 pending_campaign.whatsapp_message_id = message_id
#                 pending_campaign.state = "retry" if pending_campaign.is_retry else "sending"
#                 message = "retry" if pending_campaign.is_retry else "sending"
#                 campaign_message = f"**Campaign Message** id:{pending_campaign.access_token}; message_id:{message_id}"
#                 crud.channel.store_chat(db, pending_campaign.company_id, pending_campaign.assistant_id,
#                                         "whatsapp", None, campaign_message, pending_campaign.contact_number)
#             else:
#                 pending_campaign.state = "retry" if pending_campaign.is_retry else "failed"
#                 message = response.text if response.text else "Internal Server Error"
#             if pending_campaign.is_retry:
#                 pending_campaign.retry_count += 1
#             db.commit()
#             db.refresh(pending_campaign)
#             campaign_message_state = CampaignMessageStates(
#                 pending_campaign_handler_id=pending_campaign.id,
#                 state=pending_campaign.state,
#                 message=message
#             )
#             db.add(campaign_message_state)
#             db.commit()
#     campaign_list = list(set(campaign_list))
#     db.query(Campaigns).filter(Campaigns.id.in_(campaign_list)).update(
#         {Campaigns.status: 'In Progress'},
#         synchronize_session=False
#     )
#     db.commit()
#     db.close()
#     return {"message": "Whatsapp Messages sent successfully"}


# @celery_app.task
# def update_campaign_insights():
#     db = next(deps.get_db())
#     campaign_ids = db.query(Campaigns).order_by(Campaigns.id.asc()).all()
#     for campaign in campaign_ids:
#         if not db.query(CampaignInsights).filter(CampaignInsights.company_id == campaign.company_id,
#                                                  CampaignInsights.assistant_id == campaign.assistant_id,
#                                                  CampaignInsights.campaign_id == campaign.id).first():
#             insight_id = CampaignInsights(**{'company_id': campaign.company_id, 'assistant_id': campaign.assistant_id,
#                                              'campaign_id': campaign.id, 'total_messages': 0, 'sent_messages': 0,
#                                              'delivered_messages': 0, 'read_messages': 0, 'replied_messages': 0,
#                                              'sending_messages': 0, 'pending_messages': 0,  'retry_messages': 0,
#                                              'failed_messages': 0, 'success_ratio': 0, 'read_ratio': 0, 'replied_ratio': 0})
#             db.add(insight_id)
#             db.commit()
#             db.refresh(insight_id)
#     db.execute(text("""UPDATE campaign_insights ci
#                     SET total_messages = sub.total_messages,
#                         sent_messages = sub.sent_messages,
#                         delivered_messages = sub.delivered_messages,
#                         read_messages = sub.read_messages,
#                         replied_messages = sub.replied_messages,
#                         sending_messages = sub.sending_messages,
#                         pending_messages = sub.pending_messages,
#                         retry_messages = sub.retry_messages,
#                         failed_messages = sub.failed_messages,
#                         success_ratio = sub.success_ratio,
#                         read_ratio = sub.read_ratio,
#                         replied_ratio = sub.replied_ratio
#                     FROM   (
#                     SELECT   company_id,
#                             assistant_id,
#                             campaign_id,
#                             count(id) AS total_messages,
#                             count(id) filter(WHERE state = 'sent') AS sent_messages,
#                             count(id) filter(WHERE state = 'delivered') AS delivered_messages,
#                             count(id) filter(WHERE state = 'read') AS read_messages,
#                             count(id) filter(WHERE state = 'replied') AS replied_messages,
#                             count(id) filter(WHERE state = 'sending') AS sending_messages,
#                             count(id) filter(WHERE state = 'pending') AS pending_messages,
#                             count(id) filter(WHERE state = 'retry') AS retry_messages,
#                             count(id) filter(WHERE state = 'failed') AS failed_messages,
#                             COALESCE(
#                                 (count(id) FILTER (WHERE state = 'sent')::decimal / NULLIF(count(id), 0)) * 100, 0
#                             ) AS success_ratio,
#                             COALESCE(
#                                 (count(id) FILTER (WHERE state = 'read')::decimal / NULLIF(count(id), 0)) * 100, 0
#                             ) AS read_ratio,
#                             COALESCE(
#                                 (count(id) FILTER (WHERE state = 'replied')::decimal / NULLIF(count(id), 0)) * 100, 0
#                             ) AS replied_ratio
#                     FROM pending_campaign_handler
#                     GROUP BY company_id,
#                             assistant_id,
#                             campaign_id
#                     ) sub
#                     WHERE ci.company_id = sub.company_id
#                     AND ci.assistant_id = sub.assistant_id
#                     AND ci.campaign_id = sub.campaign_id;
#     """))
#     db.commit()
#     db.close()
#     return {"message": "Campaign Insights Computed Successfully"}


# @celery_app.task(autoretry_for=(Exception,), retry_backoff=3)
# def campaign_replied_contacts(*args, **kwargs):
#     db = next(deps.get_db())
#     contact_number = args[0]
#     pending_message = db.query(PendingCampaignHandler).filter(
#         PendingCampaignHandler.contact_number == contact_number,
#         PendingCampaignHandler.state.in_(["delivered","read"])
#     ).order_by(desc("create_date")).first()
#     if not pending_message:
#         return {"message": "No Read or Delivered Message"}
#     pending_message_state = db.query(CampaignMessageStates).filter(
#         CampaignMessageStates.pending_campaign_handler_id == pending_message.id,
#         CampaignMessageStates.state == pending_message.state
#     ).first()
#     if not pending_message_state:
#         return {"message": "Message state record not found"}
#     one_day_ago = datetime.now() - timedelta(hours=24)
#     if one_day_ago <= pending_message_state.create_date <= datetime.now():
#         pending_message.state = "replied"
#         campaign_message_state = CampaignMessageStates(
#             pending_campaign_handler_id=pending_message.id,
#             state="replied",
#             message="replied"
#         )
#         db.add(campaign_message_state)
#         db.commit()
#         db.close()
#         return {"message": "Message moved to replied state"}
#     return {"message": "No action taken"}


# @celery_app.task
# def delete_expired_campaign_document_metadata():
#     db = next(deps.get_db())
#     document_ids = db.query(DocumentMetadata).filter(DocumentMetadata.expiry_date >= datetime.now(),
#                                                      DocumentMetadata.is_from_campaign == True).all()
#     if not document_ids:
#         return {"message": "No Document Records Found"}
#     for document in document_ids:
#         if document.status == 'done':
#             vector_path = f"{os.getcwd()}/../{settings.SKLEARN_DB_PATH}/{document.company_id}/{document.assistant_id}"
#             is_deleted, _ = crud.document.delete_document_vector_celery_worker(vector_path, document.id)
#             if not is_deleted:
#                 continue
#         db.execute(text(f"DELETE FROM document_metadata WHERE id = %s"), (document.id,))
#         db.commit()
#     db.close()
#     return {"message": "Delete Expired Campaign Document Computed Successfully"}


# @celery_app.task
# def update_lead_assistant_insights():
#     db = next(deps.get_db())
#     current_datetime = datetime.now()
#     assistant_ids = db.query(Assistants).filter(
#         Assistants.function == 'Lead Generation'
#     ).order_by(Assistants.id.asc()).all()
#     for assistant in assistant_ids:
#         assistant_ids_list = [assistant.id]
#         parent_assistant_id = db.query(Assistants).filter(
#             Assistants.sub_assistant_id == assistant.id,
#             Assistants.function == 'Web Assistant'
#         ).first()
#         if parent_assistant_id:
#             assistant_ids_list.append(parent_assistant_id.id)
#         insight_id = db.query(LeadAssistantInsights).filter(
#             LeadAssistantInsights.company_id == assistant.company_id,
#             LeadAssistantInsights.assistant_id == assistant.id,
#             LeadAssistantInsights.date == current_datetime.date()
#         ).first()
#         if not insight_id:
#             insight_id = LeadAssistantInsights(
#                 company_id=assistant.company_id, assistant_id=assistant.id,
#                 date=current_datetime, total_leads=0, total_qualified_leads=0,
#                 abandoned_leads=0, total_contacts=0, lead_completion_ratio=0, duplicate_leads=0,
#                 avg_qualification_score=0, avg_time_complete_lead=0,
#                 no_exported_leads=0)
#             db.add(insight_id)
#             db.commit()
#             db.refresh(insight_id)
#         lead_info_results = (
#             db.query(
#                 (func.count(case((LeadInfo.lead_state == 'new', 1))) * 100.0 / func.nullif(
#                     func.count(case((LeadInfo.lead_state.in_(['new', 'abandoned']), 1))), 0)).label(
#                     'lead_completion_ratio'),
#                 func.avg(LeadInfo.lead_quality).label('avg_qualification_score'),
#                 func.count(case((and_(LeadInfo.lead_quality >= settings.QUALIFIED_LEAD_THRESHOLD,
#                                       LeadInfo.lead_state == 'new'), 1))).label('total_qualified_leads'),
#                 func.count(case((LeadInfo.lead_state == 'abandoned', 1))).label('abandoned_count'),
#                 func.count(case((LeadInfo.lead_state == 'contact', 1))).label('contact_count'),
#                 func.count(case((LeadInfo.lead_state == 'contact', LeadInfo.is_exported))).label('no_exported_leads'),
#                 func.count(case((LeadInfo.lead_state == 'new', 1))).label('total_leads'),
#                 func.count(case((LeadInfo.is_duplicate == True, 1))).label('duplicate_leads')
#             )
#             .filter(
#                 LeadInfo.assistant_id.in_(assistant_ids_list),
#                 LeadInfo.company_id == assistant.company_id,
#                 func.date(LeadInfo.date) == current_datetime.date()
#             ).all()
#         )
#         (lead_completion_ratio, avg_qualification_score, total_qualified_leads,
#          abandoned_leads, contacts_leads, no_exported_leads, total_leads, duplicate_leads) = lead_info_results[
#             0] if lead_info_results else (0, 0, 0, 0, 0, 0, 0, 0)
#         lead_times = (
#             select(
#                 SubAssistantEvents.event_token,
#                 func.max(
#                     case((SubAssistantEvents.event == 'lead_generation_initiated', SubAssistantEvents.date))).label(
#                     'initiated_time'),
#                 func.max(case((SubAssistantEvents.event == 'lead_generation_completed', SubAssistantEvents.date),
#                               (
#                                   SubAssistantEvents.event == 'lead_generation_abandoned',
#                                   SubAssistantEvents.date))).label(
#                     'completed_or_abandoned_time')
#             )
#             .where(
#                 SubAssistantEvents.assistant_id.in_(assistant_ids_list),
#                 SubAssistantEvents.company_id == assistant.company_id,
#                 func.date(SubAssistantEvents.date) == current_datetime.date(),
#                 SubAssistantEvents.event.in_([
#                     'lead_generation_initiated',
#                     'lead_generation_completed',
#                     'lead_generation_abandoned'
#                 ])
#             )
#             .group_by(SubAssistantEvents.event_token)
#         ).subquery()
#         avg_time_seconds_query = (
#             select(
#                 func.avg(func.extract('epoch',
#                                       lead_times.c.completed_or_abandoned_time - lead_times.c.initiated_time)).label(
#                     'avg_time_seconds')
#             )
#             .where(lead_times.c.initiated_time.isnot(None))
#             .where(lead_times.c.completed_or_abandoned_time.isnot(None))
#         )
#         avg_time_complete_lead = db.execute(avg_time_seconds_query).scalar()
#         insight_id.total_leads = total_leads
#         insight_id.total_qualified_leads = total_qualified_leads
#         insight_id.abandoned_leads = abandoned_leads
#         insight_id.total_contacts = contacts_leads
#         insight_id.duplicate_leads = duplicate_leads
#         insight_id.lead_completion_ratio = lead_completion_ratio
#         insight_id.avg_qualification_score = avg_qualification_score
#         insight_id.avg_time_complete_lead = avg_time_complete_lead
#         insight_id.no_exported_leads = no_exported_leads
#         db.commit()
#         db.refresh(insight_id)
#     db.close()
#     return {"message": "Lead Assistant Insights Computed Successfully"}


# @celery_app.task
# def update_company_insights():
#     db = next(deps.get_db())
#     current_datetime = datetime.now()
#     current_datetime_formatted = current_datetime.strftime('%Y-%m-%d')
#     company_ids = db.query(Companies).order_by(Companies.id.asc()).all()
#     for company in company_ids:
#         if not db.query(CompanyInsights).filter(CompanyInsights.company_id == company.id,
#                                                 CompanyInsights.date == current_datetime_formatted).first():
#             insight_id = CompanyInsights(**{'company_id': company.id, 'date': current_datetime_formatted,
#                                             'assistants': 0, 'helpful_answers': 0, 'not_helpful_answers': 0,
#                                             'dint_answers': 0, 'users': 0, 'sessions': 0, 'queries_session': 0,
#                                             'queries_user': 0, 'queries': 0, 'sources_found': 0, 'sources_not_found': 0,
#                                             'knowledge_base': 0})
#             db.add(insight_id)
#             db.commit()
#             db.refresh(insight_id)
#     db.execute(text(f"""UPDATE company_insights ci
#         SET helpful_answers = sub.helpful_answers, not_helpful_answers = sub.not_helpful_answers,
#         dint_answers = sub.dint_answers, users = sub.users, sessions = sub.sessions,
#         queries_session = sub.queries_session, queries_user = sub.queries_user, queries = sub.queries,
#         sources_found = sub.sources_found, sources_not_found = sub.sources_not_found
#         FROM ( SELECT company_id, TO_DATE(TO_CHAR(date, 'YYYYMMDD'), 'YYYYMMDD') AS date,
#         COUNT(is_helpful) FILTER(WHERE is_helpful = 1) AS helpful_answers,
#         COUNT(is_helpful) FILTER(WHERE is_helpful = -1) AS not_helpful_answers,
#         COUNT(is_helpful) FILTER(WHERE is_helpful = 0) AS dint_answers,
#         COUNT(DISTINCT(user_id)) AS users, COUNT(DISTINCT(session)) AS sessions,
#         (COALESCE(COUNT(question), 1) / COALESCE(NULLIF(COUNT(DISTINCT session), 0), 1)) AS queries_session,
#         (COALESCE(COUNT(question), 1) / COALESCE(NULLIF(COUNT(DISTINCT user_id), 0), 1)) AS queries_user,
#         COUNT(question) AS queries, COUNT(is_source_found) FILTER(WHERE is_source_found = 't') AS sources_found,
#         COUNT(is_source_found) FILTER(WHERE is_source_found = 'f') AS sources_not_found
#         FROM assistant_chat
#         WHERE TO_CHAR(date, 'YYYYMMDD') = '{current_datetime.strftime('%Y%m%d')}'
#         GROUP BY company_id, TO_CHAR(date, 'YYYYMMDD')) sub
#         WHERE ci.company_id = sub.company_id AND ci.date = sub.date;
#     """))
#     db.commit()
#     db.execute(text(f"""UPDATE company_insights ci SET knowledge_base = subquery.no_of_documents
#         FROM (SELECT COUNT(id) no_of_documents, company_id FROM document_metadata
#         WHERE TO_CHAR(date, 'YYYYMMDD') = \'{current_datetime.strftime('%Y%m%d')}\'
#         GROUP BY company_id) AS subquery
#         WHERE TO_CHAR(ci.date, 'YYYYMMDD') = \'{current_datetime.strftime('%Y%m%d')}\'
#         AND ci.company_id = subquery.company_id;
#     """))
#     db.commit()
#     db.execute(text(f"""UPDATE company_insights ci SET assistants = subquery.no_of_assistants
#         FROM (SELECT COUNT(id) no_of_assistants, company_id FROM assistants
#         WHERE TO_CHAR(date, 'YYYYMMDD') = \'{current_datetime.strftime('%Y%m%d')}\'
#         GROUP BY company_id) AS subquery
#         WHERE TO_CHAR(ci.date, 'YYYYMMDD') = \'{current_datetime.strftime('%Y%m%d')}\'
#         AND ci.company_id = subquery.company_id;
#     """))
#     db.commit()
#     db.close()
#     return {"message": "Company Insights Computed Successfully"}


# @celery_app.task
# def no_sources_insights():
#     db = next(deps.get_db())
#     db.query(NoSourcesInsights).delete()
#     subquery = db.query(
#         AssistantChat.company_id.label('company_id'),
#         AssistantChat.assistant_id.label('assistant_id'),
#         AssistantChat.question.label('question'),
#         func.count(AssistantChat.question).label('count'),
#         AssistantChat.is_source_found.label('is_source_found'),
#         func.row_number().over(
#             partition_by=AssistantChat.assistant_id,
#             order_by=func.count(AssistantChat.question).desc()
#         ).label('row_num')
#     ).group_by(
#         AssistantChat.company_id,
#         AssistantChat.assistant_id,
#         AssistantChat.question,
#         AssistantChat.is_source_found
#     ).subquery()
#     no_insights = db.query(subquery.c.company_id, subquery.c.assistant_id, subquery.c.question, subquery.c.count). \
#         filter(subquery.c.row_num <= 100, subquery.c.is_source_found == False). \
#         order_by(subquery.c.assistant_id, subquery.c.count.desc()).all()
#     objects = [NoSourcesInsights(company_id=row.company_id, assistant_id=row.assistant_id, question=row.question,
#                                  count=row.count) for row in no_insights]
#     db.add_all(objects)
#     db.commit()
#     db.close()
#     return {"message": "No Sources Insights Computed Successfully"}


# @celery_app.task
# def session_insights():
#     db = next(deps.get_db())
#     lead_end_date = datetime.now()
#     lead_start_date = lead_end_date - timedelta(hours=2)
#     lead_end_date_str = lead_end_date.strftime("%Y-%m-%d %H:%M:%S")
#     lead_start_date_str = lead_start_date.strftime("%Y-%m-%d %H:%M:%S")
#     db.execute(text(f"call sp_lead_channel_session_insights('{lead_start_date_str}', '{lead_end_date_str}');"))
#     db.commit()
#     current_date = lead_end_date.strftime("%Y-%m-%d")
#     db.execute(text(f"call sp_lead_assistant_session_insights('{current_date}');"))
#     db.commit()
#     db.execute(text(f"call sp_lead_url_assistant_session_insights('{current_date}');"))
#     db.commit()
#     db.execute(text(f"call sp_assistant_session_insights('{current_date}', '{current_date}');"))
#     db.commit()
#     db.execute(text(f"call sp_company_session_insights('{current_date}', '{current_date}');"))
#     db.commit()
#     db.close()
#     return {"message": f"Session Insights Computed Successfully for {current_date}"}


# @celery_app.task
# def company_statistics():
#     db = next(deps.get_db())
#     current_date = datetime.now().strftime("%Y-%m-%d")
#     company_ids = db.query(Companies).filter(Companies.is_active == True).order_by(Companies.id.desc()).all()
#     redis_client = StrictRedis(host=settings.REDIS_HOST, port=6379, db=0, decode_responses=True)
#     for company in company_ids:
#         plan_details = redis_client.hgetall(f"plan_details_{company.access_token}")
#         if not plan_details:
#             continue
#         if 'recharge_date' in plan_details:
#             plan_details.pop('recharge_date')
#         company_statistics_id = db.query(CompanyStatistics).filter(
#             CompanyStatistics.company_id == company.id).first() is not None
#         if not company_statistics_id:
#             plan_details['company_id'] = company.id
#             stat_id = CompanyStatistics(**plan_details)
#             db.add(stat_id)
#             db.commit()
#             db.refresh(stat_id)
#         else:
#             db.query(CompanyStatistics).filter(CompanyStatistics.company_id == company.id).update(plan_details)
#             db.commit()
#     db.close()
#     return {"message": f"Company Statistics Computed Successfully for {current_date}"}


# @celery_app.task
# def assistant_configurations():
#     db = next(deps.get_db())
#     current_date = datetime.now().strftime("%Y-%m-%d")
#     assistant_ids = db.query(Assistants).order_by(Assistants.id.desc()).all()
#     redis_client = StrictRedis(host=settings.REDIS_HOST, port=6379, db=0, decode_responses=True)
#     for assistant in assistant_ids:
#         config_details = redis_client.hgetall(f"{assistant.company_id}_{assistant.id}_config")
#         if not config_details:
#             continue
#         configs = {
#             'conversation_history_length': config_details.get('conversation_history_length'),
#             'initial_message': config_details.get('initial_message'),
#             'no_answer_found_response': config_details.get('no_answer_found_response'),
#             'ai_creativity_temperature': config_details.get('ai_creativity_temperature'),
#             'is_prompt_modified': eval(config_details.get('is_prompt_modified')),
#             'suggested_questions': config_details.get('suggested_questions'),
#             'bot_personality_type': config_details.get('bot_personality_type'),
#             'answer_length_category': config_details.get('answer_length_category'),
#         }
#         assistant_config_id = db.query(AssistantConfigurations).filter(
#             AssistantConfigurations.company_id == assistant.company_id,
#             AssistantConfigurations.assistant_id == assistant.id).first() is not None
#         if not assistant_config_id:
#             configs['company_id'] = assistant.company_id
#             configs['assistant_id'] = assistant.id
#             config_id = AssistantConfigurations(**configs)
#             db.add(config_id)
#             db.commit()
#             db.refresh(config_id)
#         else:
#             db.query(AssistantConfigurations).filter(
#                 AssistantConfigurations.company_id == assistant.company_id,
#                 AssistantConfigurations.assistant_id == assistant.id).update(configs)
#             db.commit()
#     db.close()
#     return {"message": f"Assistant Configurations Computed Successfully for {current_date}"}


# @celery_app.task
# def refresh_document_data_in_collection():
#     db = next(deps.get_db())
#     current_date = datetime.now()
#     document_ids = db.query(DocumentMetadata).filter(DocumentMetadata.status == 'done',
#                                                      DocumentMetadata.is_enable_refresh == True,
#                                                      DocumentMetadata.type.in_(['Website Page', 'google_drive']),
#                                                      DocumentMetadata.last_refreshed < current_date).all()
#     domain_extractor_ids = db.query(DomainExtractor).filter(DocumentMetadata.is_enable_refresh == True,
#                                                             DocumentMetadata.last_refreshed < current_date).all()
#     if not document_ids and not domain_extractor_ids:
#         return {"message": f"No Documents or DomainExtractor Records found for {current_date}"}
#     if document_ids:
#         _logger.info("Refresh Document Data Total Documents : %s" % len(document_ids))
#         for document in document_ids:
#             if document.last_refreshed + timedelta(days=int(document.refresh_frequency_days)) < current_date:
#                 new_document_id = DocumentMetadata(
#                     **{'company_id': document.company_id, 'assistant_id': document.assistant_id,
#                        'type': document.type, 'filename': document.filename, 'path': document.path,
#                        'status': 'pending', 'is_enable_refresh': document.is_enable_refresh,
#                        'refresh_frequency_days': document.refresh_frequency_days,
#                        'last_refreshed': current_date}
#                 )
#                 if new_document_id:
#                     _logger.info("Refresh Document Data Deleting old Document")
#                     vector_path = f"{os.getcwd()}/../{settings.SKLEARN_DB_PATH}/{document.company_id}/{document.assistant_id}"
#                     crud.document.delete_document_vector_celery_worker(vector_path, document.id)
#                     db.execute(text("DELETE FROM document_metadata WHERE id = %s" % (document.id)))
#                     db.add(new_document_id)
#                     db.commit()
#                     _logger.info("Refresh Document Data Training New Document")
#                     train_document.delay(new_document_id.id)
#     if domain_extractor_ids:
#         _logger.info("Refresh Document Data Total Domain Extractor : %s" % len(domain_extractor_ids))
#         for domain_extractor in domain_extractor_ids:
#             assistant_id = db.query(Assistants).filter(Assistants.id == domain_extractor.assistant_id).first()
#             if assistant_id and domain_extractor.last_refreshed + timedelta(
#                     days=int(domain_extractor.refresh_frequency_days)) < current_date:
#                 new_extractor_id = DomainExtractor(
#                     **{'assistant_id': domain_extractor.assistant_id, 'company_id': domain_extractor.company_id,
#                        'domain': domain_extractor.domain, 'deny_urls': domain_extractor.deny_urls,
#                        'is_enable_refresh': domain_extractor.is_enable_refresh, 'last_refreshed': current_date,
#                        'refresh_frequency_days': domain_extractor.refresh_frequency_days})
#                 db.add(new_extractor_id)
#                 db.commit()
#                 db.refresh(new_extractor_id)
#                 if new_extractor_id:
#                     _logger.info("Refresh Document Data Deleting old Domain Extractor")
#                     delete_website_crawler_document.delay(new_extractor_id.id)
#                     _logger.info("Refresh Document Data Creating New Domain Extractor")
#                     crud.domain_extractor.call_scrapy_api(new_extractor_id, assistant_id.access_token)
#     db.close()
#     return {"message": f"Document Refreshed Successfully for {current_date}"}
