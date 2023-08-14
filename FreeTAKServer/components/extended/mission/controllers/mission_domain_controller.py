from typing import TYPE_CHECKING
from FreeTAKServer.components.core.domain.domain import MissionInfoSingle

from FreeTAKServer.components.core.domain.domain import MissionLog
from FreeTAKServer.core.util.time_utils import get_dtg

if TYPE_CHECKING:
    from FreeTAKServer.core.enterprise_sync.persistence.sqlalchemy.enterprise_sync_keyword import EnterpriseSyncKeyword
    
    from FreeTAKServer.core.enterprise_sync.persistence.sqlalchemy.enterprise_sync_data_object import EnterpriseSyncDataObject

from FreeTAKServer.components.core.domain.domain import Event
from FreeTAKServer.components.core.domain.domain import MissionSubscription
from FreeTAKServer.core.configuration.MainConfig import MainConfig

from digitalpy.core.main.controller import Controller
from digitalpy.core.zmanager.request import Request
from digitalpy.core.zmanager.response import Response
from digitalpy.core.zmanager.action_mapper import ActionMapper
from digitalpy.core.digipy_configuration.configuration import Configuration
from digitalpy.core.parsing.load_configuration import LoadConfiguration

from FreeTAKServer.components.core.domain.domain import MissionInfo
from FreeTAKServer.components.core.domain.domain import MissionData
from FreeTAKServer.components.core.domain.domain import MissionExternalData
from FreeTAKServer.components.core.domain.domain import MissionRole
from FreeTAKServer.components.core.domain.domain import MissionContentData
from FreeTAKServer.components.core.domain.domain import MissionChangeRecord
from FreeTAKServer.components.core.domain.domain import MissionChangeRecord
from FreeTAKServer.components.core.domain.domain import MissionContent
from FreeTAKServer.components.core.domain.domain import mission as DomainMissionCot

from ..persistence.mission import Mission as DBMission
from ..persistence.mission_content import MissionContent as DBMissionContent
from ..persistence.subscription import Subscription as DBSubscription

from ..configuration.mission_constants import (
    BASE_OBJECT_NAME,
    MISSION_CONTENT,
    MISSION_EXTERNAL_DATA,
    MISSION_ITEM,
    MISSION_LOG,
    MISSION_LOG_COLLECTION,
    MISSION_RECORD,
    MISSION_SUBSCRIPTION,
    MISSION_SUBSCRIPTION_DATA,
    MISSION_NOTIFICATION,
    MISSION_COLLECTION,
    MISSION_SUBSCRIPTION_LIST,
    MISSION_SUBSCRIPTION_SIMPLE_LIST,
    MISSION_CHANGE_RECORD,
    MISSION_CONTENT_DATA
)

config = MainConfig.instance()

class MissionDomainController(Controller):
    """manage operations related to mission domain"""
    def __init__(self, request: Request, response: Response, sync_action_mapper: ActionMapper, configuration: Configuration):
        super().__init__(request, response, sync_action_mapper, configuration)
        
    def initialize(self, request, response):
        super().initialize(request, response)
    
    def execute(self, method=None):
        getattr(self, method)(**self.request.get_values())
        return self.response
    
    def create_mission_change_record(self, config_loader, *args, **kwargs) -> MissionChangeRecord:
        """create a new mission change record"""
        self.request.set_value("object_class_name", "MissionChangeRecord")

        configuration = config_loader.find_configuration(MISSION_CHANGE_RECORD)

        self.request.set_value("configuration", configuration)

        self.request.set_value(
            "source_format", self.request.get_value("source_format")
        )
        self.request.set_value("target_format", "node")

        response = self.execute_sub_action("CreateNode")

        return response.get_value("model_object")

    def create_mission_collection(self, config_loader, *args, **kwargs) -> MissionInfo:
        """create a new empty mission collection"""
        self.request.set_value("object_class_name", "MissionInfo")
        
        configuration = config_loader.find_configuration(MISSION_COLLECTION)
        
        self.request.set_value("configuration", configuration)

        self.request.set_value(
            "source_format", self.request.get_value("source_format")
        )
        self.request.set_value("target_format", "node")

        response = self.execute_sub_action("CreateNode")

        mission_collection: MissionInfo = response.get_value("model_object")
        
        mission_collection.version = "3"
        mission_collection.type = "Mission"
        mission_collection.nodeId = config.nodeID
        
        return response.get_value("model_object")
    
    def add_mission_to_collection(self, mission_collection:MissionInfo, mission_record:MissionData, *args, **kwargs) -> MissionData:
        """add a mission record to a mission collection"""
        mission_collection.data = mission_record
        return mission_collection
        
    def create_mission_record_object(self, config_loader: LoadConfiguration, **kwargs):
        """create a new mission subscription object"""
        self.request.set_value("object_class_name", "MissionData")

        configuration = config_loader.find_configuration(MISSION_RECORD)

        self.request.set_value("configuration", configuration)

        self.request.set_value("extended_domain", {"MissionData": MissionData, "MissionContent": MissionContent, "MissionContentData": MissionContentData, "MissionExternalData": MissionExternalData, "MissionRole": MissionRole})

        self.request.set_value(
            "source_format", self.request.get_value("source_format")
        )
        self.request.set_value("target_format", "node")

        response = self.execute_sub_action("CreateNode")

        return response.get_value("model_object")
    
    def complete_mission_record_db(self, mission_domain_object: MissionData, mission_db_object: DBMission, config_loader, subscription: DBSubscription = None, **kwargs) -> MissionData: # type: ignore
        """complete the mission record from a db object"""
        # complete the mission record db object
        mission_domain_object.name = mission_db_object.PrimaryKey
        mission_domain_object.description = mission_db_object.description
        mission_domain_object.chatRoom = mission_db_object.chatRoom
        mission_domain_object.baseLayer = mission_db_object.baseLayer
        mission_domain_object.bbox = mission_db_object.bbox
        mission_domain_object.path = mission_db_object.path
        mission_domain_object.classification = mission_db_object.classification
        mission_domain_object.tool = "public"
        mission_domain_object.keywords = []
        mission_domain_object.creatorUid = mission_db_object.creatorUid
        # TODO: get time dynamically
        mission_domain_object.createTime = get_dtg(mission_db_object.createTime)
        # mission_domain_object.groups = mission_db_object.groups
        mission_domain_object.groups = []
        # mission_domain_object.externalData = mission_db_object.externalData
        
        # mission_domain_object.feeds = mission_db_object.feeds
        mission_domain_object.feeds = []
        # mission_domain_object.mapLayers = mission_db_object.mapLayers
        mission_domain_object.mapLayers = []
        mission_domain_object.inviteOnly = mission_db_object.inviteOnly
        mission_domain_object.expiration = mission_db_object.expiration
        # mission_domain_object.uids = mission_db_object.uids
        mission_domain_object.uids = []
        mission_domain_object.passwordProtected = mission_db_object.passwordProtected
        
        for db_content in mission_db_object.contents:
            domain_content = self.create_mission_content(config_loader)
            mission_domain_object.contents = self.complete_mission_content_db(domain_content, db_content)
        
        #add the contents of all children to the mission
        for child in mission_db_object.child_missions:
            for db_content in child.child_mission.contents:
                domain_content = self.create_mission_content(config_loader)
                mission_domain_object.contents = self.complete_mission_content_db(domain_content, db_content)
        
        if subscription is not None:
            mission_domain_object.token = subscription.token
        
        return mission_domain_object
    
    def create_mission_creation_notification(self, config_loader,*args, **kwargs):
        """create a new mission notification object"""
        self.request.set_value("object_class_name", "Event")

        configuration = config_loader.find_configuration(MISSION_NOTIFICATION)

        self.request.set_value("configuration", configuration)

        self.request.set_value("extended_domain", {"mission": DomainMissionCot})

        self.request.set_value(
            "source_format", self.request.get_value("source_format")
        )
        self.request.set_value("target_format", "node")

        response = self.execute_sub_action("CreateNode")

        model_object = response.get_value("model_object")

        return model_object
    
    def complete_mission_content_db(self, mission_content_domain: MissionContent, mission_content_db: DBMissionContent, *args, **kwargs) -> MissionContent:
        self.request.set_value("objectuid", mission_content_db.PrimaryKey)
        self.request.set_value("objecthash", mission_content_db.PrimaryKey)
        
        enterprise_sync_db: 'EnterpriseSyncDataObject' = self.execute_sub_action("GetEnterpriseSyncMetaData").get_value("objectmetadata")
        
        mission_content_domain.timestamp = get_dtg(enterprise_sync_db.start_time)
        mission_content_domain.creatorUid = enterprise_sync_db.creator_uid
        
        self.complete_mission_content_data(mission_content_domain.data, enterprise_sync_db)

        return mission_content_domain

    def complete_mission_content_data(self, mission_content_data_domain: MissionContentData, mission_content_db: 'EnterpriseSyncDataObject') -> MissionContentData:
        mission_content_data_domain.uid = mission_content_db.PrimaryKey
        mission_content_data_domain.hash = mission_content_db.hash
        mission_content_data_domain.name = mission_content_db.file_name
        mission_content_data_domain.mimeType = mission_content_db.mime_type
        mission_content_data_domain.size = mission_content_db.length
        mission_content_data_domain.tool = mission_content_db.tool
        mission_content_data_domain.submitter = mission_content_db.submitter
        
        keywords = []
        for keyword in mission_content_db.keywords:
            keywords.append(keyword.keyword)
            
        mission_content_data_domain.keywords = keywords
        mission_content_data_domain.expiration = mission_content_db.expiration
        return mission_content_data_domain

    def complete_mission_creation_notification(self, mission_notification: Event, mission: MissionData, *args, **kwargs) -> Event:
        """complete a mission creation notification object based on a mission domain object

        Args:
            mission_notification (Event): the mission notification object to complete
            mission (MissionData): the mission domain object to use for completion
        """
        mission_notification.type = "t-x-m-n" # type: ignore
        mission_notification.how = "h-g-i-g-o" # type: ignore
        mission_notification.detail.mission.type = "CREATE" # type: ignore
        mission_notification.detail.mission.tool = "public" # type: ignore
        mission_notification.detail.mission.name = mission.name # type: ignore
        mission_notification.detail.mission.authorUid = mission.creatorUid # type: ignore
        
        return mission_notification
    
    def create_mission_subscription_simple_list(self, config_loader, *args, **kwargs) -> MissionInfo:
        """return the domain object used to show all the subscription ids in a mission"""
        self.request.set_value("object_class_name", "MissionInfo")

        configuration = config_loader.find_configuration(MISSION_SUBSCRIPTION_SIMPLE_LIST)

        self.request.set_value("configuration", configuration)

        self.request.set_value("extended_domain", {"MissionInfo": MissionInfo})

        self.request.set_value(
            "source_format", self.request.get_value("source_format")
        )
        self.request.set_value("target_format", "node")

        response = self.execute_sub_action("CreateNode")

        model_object = response.get_value("model_object")

        return model_object
    
    def create_mission_subscriptions_list(self, config_loader, *args, **kwargs) -> MissionInfo:
        """return the domain object used to show all the subscriptions and roles in a mission"""
        self.request.set_value("object_class_name", "MissionInfo")

        configuration = config_loader.find_configuration(MISSION_SUBSCRIPTION_LIST)

        self.request.set_value("configuration", configuration)

        self.request.set_value("extended_domain", {"MissionInfo": MissionInfo, "MissionSubscription": MissionSubscription, "MissionRole": MissionRole})

        self.request.set_value(
            "source_format", self.request.get_value("source_format")
        )
        self.request.set_value("target_format", "node")

        response = self.execute_sub_action("CreateNode")

        model_object = response.get_value("model_object")

        return model_object
    
    def create_mission_subscription(self, config_loader, *args, **kwargs) ->MissionInfoSingle:
        """return the domain object used a subscription in a mission"""
        self.request.set_value("object_class_name", "MissionInfoSingle")

        configuration = config_loader.find_configuration(MISSION_SUBSCRIPTION)

        self.request.set_value("configuration", configuration)

        self.request.set_value("extended_domain", {"MissionInfoSingle": MissionInfoSingle, "MissionSubscription": MissionSubscription, "MissionRole": MissionRole})

        self.request.set_value(
            "source_format", self.request.get_value("source_format")
        )
        self.request.set_value("target_format", "node")

        response = self.execute_sub_action("CreateNode")

        model_object = response.get_value("model_object")

        return model_object
    
    def create_mission_subscription_data(self, config_loader, *args, **kwargs) -> MissionSubscription:
        """return the domain object used to show all the subscriptions in a mission"""
        self.request.set_value("object_class_name", "MissionSubscription")

        configuration = config_loader.find_configuration(MISSION_SUBSCRIPTION_DATA)

        self.request.set_value("configuration", configuration)

        self.request.set_value("extended_domain", {"MissionSubscription": MissionSubscription, "MissionRole": MissionRole})

        self.request.set_value(
            "source_format", self.request.get_value("source_format")
        )
        self.request.set_value("target_format", "node")

        response = self.execute_sub_action("CreateNode")

        model_object = response.get_value("model_object")

        return model_object
    
    def create_mission_content(self, config_loader, *args, **kwargs) -> MissionContent:
        """return the domain object used a content entry in a mission"""
        self.request.set_value("object_class_name", "MissionContent")

        configuration = config_loader.find_configuration(MISSION_CONTENT)

        self.request.set_value("configuration", configuration)

        self.request.set_value("extended_domain", {"MissionContent": MissionContent, "MissionContentData": MissionContentData})

        self.request.set_value(
            "source_format", self.request.get_value("source_format")
        )
        self.request.set_value("target_format", "node")

        response = self.execute_sub_action("CreateNode")

        model_object = response.get_value("model_object")

        return model_object
    
    def create_mission_content_data(self, config_loader, *args, **kwargs) -> MissionContentData:
        """return the domain object used a content entry in a mission"""
        self.request.set_value("object_class_name", "MissionContentData")

        configuration = config_loader.find_configuration(MISSION_CONTENT_DATA)

        self.request.set_value("configuration", configuration)

        self.request.set_value("extended_domain", {"MissionContentData": MissionContentData})

        self.request.set_value(
            "source_format", self.request.get_value("source_format")
        )
        self.request.set_value("target_format", "node")

        response = self.execute_sub_action("CreateNode")

        model_object = response.get_value("model_object")

        return model_object
    
    def create_log(self, config_loader, *args, **kwargs) -> MissionLog:
        """return the domain object used a log entry in a mission"""
        self.request.set_value("object_class_name", "MissionLog")

        configuration = config_loader.find_configuration(MISSION_LOG)

        self.request.set_value("configuration", configuration)

        self.request.set_value("extended_domain", {"MissionLog": MissionLog})

        self.request.set_value(
            "source_format", self.request.get_value("source_format")
        )
        self.request.set_value("target_format", "node")

        response = self.execute_sub_action("CreateNode")

        model_object = response.get_value("model_object")

        return model_object
    
    def create_log_collection(self, config_loader, *args, **kwargs) -> MissionInfo:
        self.request.set_value("object_class_name", "MissionInfo")
        
        configuration = config_loader.find_configuration(MISSION_LOG_COLLECTION)

        self.request.set_value("configuration", configuration)

        self.request.set_value("extended_domain", {"MissionInfo": MissionInfo, "MissionLog": MissionLog})

        self.request.set_value(
            "source_format", self.request.get_value("source_format")
        )
        self.request.set_value("target_format", "node")
        
        response = self.execute_sub_action("CreateNode")
        
        model_object = response.get_value("model_object")

        return model_object
    
    def create_external_data_collection(self, config_loader, *args, **kwargs) -> MissionInfoSingle:
        """return the domain object used a external data entry in a mission"""
        self.request.set_value("object_class_name", "MissionInfoSingle")

        configuration = config_loader.find_configuration(MISSION_EXTERNAL_DATA)

        self.request.set_value("configuration", configuration)

        self.request.set_value("extended_domain", {"MissionExternalData": MissionExternalData, "MissionInfoSingle": MissionInfoSingle})

        self.request.set_value(
            "source_format", self.request.get_value("source_format")
        )
        self.request.set_value("target_format", "node")

        response = self.execute_sub_action("CreateNode")

        model_object = response.get_value("model_object")

        return model_object
    
    def create_external_data(self, config_loader, *args, **kwargs) -> MissionExternalData:
        """return the domain object used a external data entry in a mission"""
        self.request.set_value("object_class_name", "MissionExternalData")

        configuration = config_loader.find_configuration(MISSION_EXTERNAL_DATA)

        self.request.set_value("configuration", configuration)

        self.request.set_value("extended_domain", {"MissionExternalData": MissionExternalData})

        self.request.set_value(
            "source_format", self.request.get_value("source_format")
        )
        self.request.set_value("target_format", "node")

        response = self.execute_sub_action("CreateNode")

        model_object = response.get_value("model_object")

        return model_object