---
name: lap-alexa-for-business
description: "Alexa For Business API skill. Use when working with Alexa For Business for #X-Amz-Target=AlexaForBusiness.ApproveSkill, #X-Amz-Target=AlexaForBusiness.AssociateContactWithAddressBook, #X-Amz-Target=AlexaForBusiness.AssociateDeviceWithNetworkProfile. Covers 93 endpoints."
version: 1.0.0
generator: lapsh
metadata:
  openclaw:
    requires:
      env:
        - ALEXA_FOR_BUSINESS_API_KEY
---

# Alexa For Business
API version: 2017-11-09

## Auth
ApiKey Authorization in header

## Base URL
http://a4b.{region}.amazonaws.com

## Setup
1. Set your API key in the appropriate header
3. POST /#X-Amz-Target=AlexaForBusiness.ApproveSkill -- create first #X-Amz-Target=AlexaForBusiness.ApproveSkill

## Endpoints

93 endpoints across 93 groups. See references/api-spec.lap for full details.

### #X-Amz-Target=AlexaForBusiness.ApproveSkill
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.ApproveSkill | Associates a skill with the organization under the customer's AWS account. If a skill is private, the user implicitly accepts access to this skill during enablement. |

### #X-Amz-Target=AlexaForBusiness.AssociateContactWithAddressBook
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.AssociateContactWithAddressBook | Associates a contact with a given address book. |

### #X-Amz-Target=AlexaForBusiness.AssociateDeviceWithNetworkProfile
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.AssociateDeviceWithNetworkProfile | Associates a device with the specified network profile. |

### #X-Amz-Target=AlexaForBusiness.AssociateDeviceWithRoom
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.AssociateDeviceWithRoom | Associates a device with a given room. This applies all the settings from the room profile to the device, and all the skills in any skill groups added to that room. This operation requires the device to be online, or else a manual sync is required. |

### #X-Amz-Target=AlexaForBusiness.AssociateSkillGroupWithRoom
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.AssociateSkillGroupWithRoom | Associates a skill group with a given room. This enables all skills in the associated skill group on all devices in the room. |

### #X-Amz-Target=AlexaForBusiness.AssociateSkillWithSkillGroup
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.AssociateSkillWithSkillGroup | Associates a skill with a skill group. |

### #X-Amz-Target=AlexaForBusiness.AssociateSkillWithUsers
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.AssociateSkillWithUsers | Makes a private skill available for enrolled users to enable on their devices. |

### #X-Amz-Target=AlexaForBusiness.CreateAddressBook
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.CreateAddressBook | Creates an address book with the specified details. |

### #X-Amz-Target=AlexaForBusiness.CreateBusinessReportSchedule
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.CreateBusinessReportSchedule | Creates a recurring schedule for usage reports to deliver to the specified S3 location with a specified daily or weekly interval. |

### #X-Amz-Target=AlexaForBusiness.CreateConferenceProvider
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.CreateConferenceProvider | Adds a new conference provider under the user's AWS account. |

### #X-Amz-Target=AlexaForBusiness.CreateContact
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.CreateContact | Creates a contact with the specified details. |

### #X-Amz-Target=AlexaForBusiness.CreateGatewayGroup
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.CreateGatewayGroup | Creates a gateway group with the specified details. |

### #X-Amz-Target=AlexaForBusiness.CreateNetworkProfile
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.CreateNetworkProfile | Creates a network profile with the specified details. |

### #X-Amz-Target=AlexaForBusiness.CreateProfile
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.CreateProfile | Creates a new room profile with the specified details. |

### #X-Amz-Target=AlexaForBusiness.CreateRoom
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.CreateRoom | Creates a room with the specified details. |

### #X-Amz-Target=AlexaForBusiness.CreateSkillGroup
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.CreateSkillGroup | Creates a skill group with a specified name and description. |

### #X-Amz-Target=AlexaForBusiness.CreateUser
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.CreateUser | Creates a user. |

### #X-Amz-Target=AlexaForBusiness.DeleteAddressBook
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.DeleteAddressBook | Deletes an address book by the address book ARN. |

### #X-Amz-Target=AlexaForBusiness.DeleteBusinessReportSchedule
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.DeleteBusinessReportSchedule | Deletes the recurring report delivery schedule with the specified schedule ARN. |

### #X-Amz-Target=AlexaForBusiness.DeleteConferenceProvider
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.DeleteConferenceProvider | Deletes a conference provider. |

### #X-Amz-Target=AlexaForBusiness.DeleteContact
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.DeleteContact | Deletes a contact by the contact ARN. |

### #X-Amz-Target=AlexaForBusiness.DeleteDevice
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.DeleteDevice | Removes a device from Alexa For Business. |

### #X-Amz-Target=AlexaForBusiness.DeleteDeviceUsageData
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.DeleteDeviceUsageData | When this action is called for a specified shared device, it allows authorized users to delete the device's entire previous history of voice input data and associated response data. This action can be called once every 24 hours for a specific shared device. |

### #X-Amz-Target=AlexaForBusiness.DeleteGatewayGroup
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.DeleteGatewayGroup | Deletes a gateway group. |

### #X-Amz-Target=AlexaForBusiness.DeleteNetworkProfile
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.DeleteNetworkProfile | Deletes a network profile by the network profile ARN. |

### #X-Amz-Target=AlexaForBusiness.DeleteProfile
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.DeleteProfile | Deletes a room profile by the profile ARN. |

### #X-Amz-Target=AlexaForBusiness.DeleteRoom
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.DeleteRoom | Deletes a room by the room ARN. |

### #X-Amz-Target=AlexaForBusiness.DeleteRoomSkillParameter
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.DeleteRoomSkillParameter | Deletes room skill parameter details by room, skill, and parameter key ID. |

### #X-Amz-Target=AlexaForBusiness.DeleteSkillAuthorization
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.DeleteSkillAuthorization | Unlinks a third-party account from a skill. |

### #X-Amz-Target=AlexaForBusiness.DeleteSkillGroup
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.DeleteSkillGroup | Deletes a skill group by skill group ARN. |

### #X-Amz-Target=AlexaForBusiness.DeleteUser
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.DeleteUser | Deletes a specified user by user ARN and enrollment ARN. |

### #X-Amz-Target=AlexaForBusiness.DisassociateContactFromAddressBook
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.DisassociateContactFromAddressBook | Disassociates a contact from a given address book. |

### #X-Amz-Target=AlexaForBusiness.DisassociateDeviceFromRoom
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.DisassociateDeviceFromRoom | Disassociates a device from its current room. The device continues to be connected to the Wi-Fi network and is still registered to the account. The device settings and skills are removed from the room. |

### #X-Amz-Target=AlexaForBusiness.DisassociateSkillFromSkillGroup
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.DisassociateSkillFromSkillGroup | Disassociates a skill from a skill group. |

### #X-Amz-Target=AlexaForBusiness.DisassociateSkillFromUsers
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.DisassociateSkillFromUsers | Makes a private skill unavailable for enrolled users and prevents them from enabling it on their devices. |

### #X-Amz-Target=AlexaForBusiness.DisassociateSkillGroupFromRoom
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.DisassociateSkillGroupFromRoom | Disassociates a skill group from a specified room. This disables all skills in the skill group on all devices in the room. |

### #X-Amz-Target=AlexaForBusiness.ForgetSmartHomeAppliances
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.ForgetSmartHomeAppliances | Forgets smart home appliances associated to a room. |

### #X-Amz-Target=AlexaForBusiness.GetAddressBook
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.GetAddressBook | Gets address the book details by the address book ARN. |

### #X-Amz-Target=AlexaForBusiness.GetConferencePreference
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.GetConferencePreference | Retrieves the existing conference preferences. |

### #X-Amz-Target=AlexaForBusiness.GetConferenceProvider
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.GetConferenceProvider | Gets details about a specific conference provider. |

### #X-Amz-Target=AlexaForBusiness.GetContact
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.GetContact | Gets the contact details by the contact ARN. |

### #X-Amz-Target=AlexaForBusiness.GetDevice
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.GetDevice | Gets the details of a device by device ARN. |

### #X-Amz-Target=AlexaForBusiness.GetGateway
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.GetGateway | Retrieves the details of a gateway. |

### #X-Amz-Target=AlexaForBusiness.GetGatewayGroup
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.GetGatewayGroup | Retrieves the details of a gateway group. |

### #X-Amz-Target=AlexaForBusiness.GetInvitationConfiguration
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.GetInvitationConfiguration | Retrieves the configured values for the user enrollment invitation email template. |

### #X-Amz-Target=AlexaForBusiness.GetNetworkProfile
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.GetNetworkProfile | Gets the network profile details by the network profile ARN. |

### #X-Amz-Target=AlexaForBusiness.GetProfile
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.GetProfile | Gets the details of a room profile by profile ARN. |

### #X-Amz-Target=AlexaForBusiness.GetRoom
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.GetRoom | Gets room details by room ARN. |

### #X-Amz-Target=AlexaForBusiness.GetRoomSkillParameter
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.GetRoomSkillParameter | Gets room skill parameter details by room, skill, and parameter key ARN. |

### #X-Amz-Target=AlexaForBusiness.GetSkillGroup
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.GetSkillGroup | Gets skill group details by skill group ARN. |

### #X-Amz-Target=AlexaForBusiness.ListBusinessReportSchedules
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.ListBusinessReportSchedules | Lists the details of the schedules that a user configured. A download URL of the report associated with each schedule is returned every time this action is called. A new download URL is returned each time, and is valid for 24 hours. |

### #X-Amz-Target=AlexaForBusiness.ListConferenceProviders
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.ListConferenceProviders | Lists conference providers under a specific AWS account. |

### #X-Amz-Target=AlexaForBusiness.ListDeviceEvents
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.ListDeviceEvents | Lists the device event history, including device connection status, for up to 30 days. |

### #X-Amz-Target=AlexaForBusiness.ListGatewayGroups
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.ListGatewayGroups | Retrieves a list of gateway group summaries. Use GetGatewayGroup to retrieve details of a specific gateway group. |

### #X-Amz-Target=AlexaForBusiness.ListGateways
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.ListGateways | Retrieves a list of gateway summaries. Use GetGateway to retrieve details of a specific gateway. An optional gateway group ARN can be provided to only retrieve gateway summaries of gateways that are associated with that gateway group ARN. |

### #X-Amz-Target=AlexaForBusiness.ListSkills
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.ListSkills | Lists all enabled skills in a specific skill group. |

### #X-Amz-Target=AlexaForBusiness.ListSkillsStoreCategories
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.ListSkillsStoreCategories | Lists all categories in the Alexa skill store. |

### #X-Amz-Target=AlexaForBusiness.ListSkillsStoreSkillsByCategory
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.ListSkillsStoreSkillsByCategory | Lists all skills in the Alexa skill store by category. |

### #X-Amz-Target=AlexaForBusiness.ListSmartHomeAppliances
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.ListSmartHomeAppliances | Lists all of the smart home appliances associated with a room. |

### #X-Amz-Target=AlexaForBusiness.ListTags
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.ListTags | Lists all tags for the specified resource. |

### #X-Amz-Target=AlexaForBusiness.PutConferencePreference
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.PutConferencePreference | Sets the conference preferences on a specific conference provider at the account level. |

### #X-Amz-Target=AlexaForBusiness.PutInvitationConfiguration
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.PutInvitationConfiguration | Configures the email template for the user enrollment invitation with the specified attributes. |

### #X-Amz-Target=AlexaForBusiness.PutRoomSkillParameter
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.PutRoomSkillParameter | Updates room skill parameter details by room, skill, and parameter key ID. Not all skills have a room skill parameter. |

### #X-Amz-Target=AlexaForBusiness.PutSkillAuthorization
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.PutSkillAuthorization | Links a user's account to a third-party skill provider. If this API operation is called by an assumed IAM role, the skill being linked must be a private skill. Also, the skill must be owned by the AWS account that assumed the IAM role. |

### #X-Amz-Target=AlexaForBusiness.RegisterAVSDevice
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.RegisterAVSDevice | Registers an Alexa-enabled device built by an Original Equipment Manufacturer (OEM) using Alexa Voice Service (AVS). |

### #X-Amz-Target=AlexaForBusiness.RejectSkill
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.RejectSkill | Disassociates a skill from the organization under a user's AWS account. If the skill is a private skill, it moves to an AcceptStatus of PENDING. Any private or public skill that is rejected can be added later by calling the ApproveSkill API. |

### #X-Amz-Target=AlexaForBusiness.ResolveRoom
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.ResolveRoom | Determines the details for the room from which a skill request was invoked. This operation is used by skill developers. To query ResolveRoom from an Alexa skill, the skill ID needs to be authorized. When the skill is using an AWS Lambda function, the skill is automatically authorized when you publish your skill as a private skill to your AWS account. Skills that are hosted using a custom web service must be manually authorized. To get your skill authorized, contact AWS Support with your AWS account ID that queries the ResolveRoom API and skill ID. |

### #X-Amz-Target=AlexaForBusiness.RevokeInvitation
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.RevokeInvitation | Revokes an invitation and invalidates the enrollment URL. |

### #X-Amz-Target=AlexaForBusiness.SearchAddressBooks
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.SearchAddressBooks | Searches address books and lists the ones that meet a set of filter and sort criteria. |

### #X-Amz-Target=AlexaForBusiness.SearchContacts
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.SearchContacts | Searches contacts and lists the ones that meet a set of filter and sort criteria. |

### #X-Amz-Target=AlexaForBusiness.SearchDevices
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.SearchDevices | Searches devices and lists the ones that meet a set of filter criteria. |

### #X-Amz-Target=AlexaForBusiness.SearchNetworkProfiles
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.SearchNetworkProfiles | Searches network profiles and lists the ones that meet a set of filter and sort criteria. |

### #X-Amz-Target=AlexaForBusiness.SearchProfiles
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.SearchProfiles | Searches room profiles and lists the ones that meet a set of filter criteria. |

### #X-Amz-Target=AlexaForBusiness.SearchRooms
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.SearchRooms | Searches rooms and lists the ones that meet a set of filter and sort criteria. |

### #X-Amz-Target=AlexaForBusiness.SearchSkillGroups
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.SearchSkillGroups | Searches skill groups and lists the ones that meet a set of filter and sort criteria. |

### #X-Amz-Target=AlexaForBusiness.SearchUsers
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.SearchUsers | Searches users and lists the ones that meet a set of filter and sort criteria. |

### #X-Amz-Target=AlexaForBusiness.SendAnnouncement
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.SendAnnouncement | Triggers an asynchronous flow to send text, SSML, or audio announcements to rooms that are identified by a search or filter. |

### #X-Amz-Target=AlexaForBusiness.SendInvitation
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.SendInvitation | Sends an enrollment invitation email with a URL to a user. The URL is valid for 30 days or until you call this operation again, whichever comes first. |

### #X-Amz-Target=AlexaForBusiness.StartDeviceSync
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.StartDeviceSync | Resets a device and its account to the known default settings. This clears all information and settings set by previous users in the following ways:   Bluetooth - This unpairs all bluetooth devices paired with your echo device.   Volume - This resets the echo device's volume to the default value.   Notifications - This clears all notifications from your echo device.   Lists - This clears all to-do items from your echo device.   Settings - This internally syncs the room's profile (if the device is assigned to a room), contacts, address books, delegation access for account linking, and communications (if enabled on the room profile). |

### #X-Amz-Target=AlexaForBusiness.StartSmartHomeApplianceDiscovery
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.StartSmartHomeApplianceDiscovery | Initiates the discovery of any smart home appliances associated with the room. |

### #X-Amz-Target=AlexaForBusiness.TagResource
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.TagResource | Adds metadata tags to a specified resource. |

### #X-Amz-Target=AlexaForBusiness.UntagResource
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.UntagResource | Removes metadata tags from a specified resource. |

### #X-Amz-Target=AlexaForBusiness.UpdateAddressBook
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.UpdateAddressBook | Updates address book details by the address book ARN. |

### #X-Amz-Target=AlexaForBusiness.UpdateBusinessReportSchedule
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.UpdateBusinessReportSchedule | Updates the configuration of the report delivery schedule with the specified schedule ARN. |

### #X-Amz-Target=AlexaForBusiness.UpdateConferenceProvider
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.UpdateConferenceProvider | Updates an existing conference provider's settings. |

### #X-Amz-Target=AlexaForBusiness.UpdateContact
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.UpdateContact | Updates the contact details by the contact ARN. |

### #X-Amz-Target=AlexaForBusiness.UpdateDevice
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.UpdateDevice | Updates the device name by device ARN. |

### #X-Amz-Target=AlexaForBusiness.UpdateGateway
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.UpdateGateway | Updates the details of a gateway. If any optional field is not provided, the existing corresponding value is left unmodified. |

### #X-Amz-Target=AlexaForBusiness.UpdateGatewayGroup
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.UpdateGatewayGroup | Updates the details of a gateway group. If any optional field is not provided, the existing corresponding value is left unmodified. |

### #X-Amz-Target=AlexaForBusiness.UpdateNetworkProfile
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.UpdateNetworkProfile | Updates a network profile by the network profile ARN. |

### #X-Amz-Target=AlexaForBusiness.UpdateProfile
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.UpdateProfile | Updates an existing room profile by room profile ARN. |

### #X-Amz-Target=AlexaForBusiness.UpdateRoom
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.UpdateRoom | Updates room details by room ARN. |

### #X-Amz-Target=AlexaForBusiness.UpdateSkillGroup
| Method | Path | Description |
|--------|------|-------------|
| POST | /#X-Amz-Target=AlexaForBusiness.UpdateSkillGroup | Updates skill group details by skill group ARN. |

## Common Questions

Match user requests to endpoints in references/api-spec.lap. Key patterns:
- "Create a #X-Amz-Target=AlexaForBusiness.ApproveSkill?" -> POST /#X-Amz-Target=AlexaForBusiness.ApproveSkill
- "Create a #X-Amz-Target=AlexaForBusiness.AssociateContactWithAddressBook?" -> POST /#X-Amz-Target=AlexaForBusiness.AssociateContactWithAddressBook
- "Create a #X-Amz-Target=AlexaForBusiness.AssociateDeviceWithNetworkProfile?" -> POST /#X-Amz-Target=AlexaForBusiness.AssociateDeviceWithNetworkProfile
- "Create a #X-Amz-Target=AlexaForBusiness.AssociateDeviceWithRoom?" -> POST /#X-Amz-Target=AlexaForBusiness.AssociateDeviceWithRoom
- "Create a #X-Amz-Target=AlexaForBusiness.AssociateSkillGroupWithRoom?" -> POST /#X-Amz-Target=AlexaForBusiness.AssociateSkillGroupWithRoom
- "Create a #X-Amz-Target=AlexaForBusiness.AssociateSkillWithSkillGroup?" -> POST /#X-Amz-Target=AlexaForBusiness.AssociateSkillWithSkillGroup
- "Create a #X-Amz-Target=AlexaForBusiness.AssociateSkillWithUser?" -> POST /#X-Amz-Target=AlexaForBusiness.AssociateSkillWithUsers
- "Create a #X-Amz-Target=AlexaForBusiness.CreateAddressBook?" -> POST /#X-Amz-Target=AlexaForBusiness.CreateAddressBook
- "Create a #X-Amz-Target=AlexaForBusiness.CreateBusinessReportSchedule?" -> POST /#X-Amz-Target=AlexaForBusiness.CreateBusinessReportSchedule
- "Create a #X-Amz-Target=AlexaForBusiness.CreateConferenceProvider?" -> POST /#X-Amz-Target=AlexaForBusiness.CreateConferenceProvider
- "Create a #X-Amz-Target=AlexaForBusiness.CreateContact?" -> POST /#X-Amz-Target=AlexaForBusiness.CreateContact
- "Create a #X-Amz-Target=AlexaForBusiness.CreateGatewayGroup?" -> POST /#X-Amz-Target=AlexaForBusiness.CreateGatewayGroup
- "Create a #X-Amz-Target=AlexaForBusiness.CreateNetworkProfile?" -> POST /#X-Amz-Target=AlexaForBusiness.CreateNetworkProfile
- "Create a #X-Amz-Target=AlexaForBusiness.CreateProfile?" -> POST /#X-Amz-Target=AlexaForBusiness.CreateProfile
- "Create a #X-Amz-Target=AlexaForBusiness.CreateRoom?" -> POST /#X-Amz-Target=AlexaForBusiness.CreateRoom
- "Create a #X-Amz-Target=AlexaForBusiness.CreateSkillGroup?" -> POST /#X-Amz-Target=AlexaForBusiness.CreateSkillGroup
- "Create a #X-Amz-Target=AlexaForBusiness.CreateUser?" -> POST /#X-Amz-Target=AlexaForBusiness.CreateUser
- "Create a #X-Amz-Target=AlexaForBusiness.DeleteAddressBook?" -> POST /#X-Amz-Target=AlexaForBusiness.DeleteAddressBook
- "Create a #X-Amz-Target=AlexaForBusiness.DeleteBusinessReportSchedule?" -> POST /#X-Amz-Target=AlexaForBusiness.DeleteBusinessReportSchedule
- "Create a #X-Amz-Target=AlexaForBusiness.DeleteConferenceProvider?" -> POST /#X-Amz-Target=AlexaForBusiness.DeleteConferenceProvider
- "Create a #X-Amz-Target=AlexaForBusiness.DeleteContact?" -> POST /#X-Amz-Target=AlexaForBusiness.DeleteContact
- "Create a #X-Amz-Target=AlexaForBusiness.DeleteDevice?" -> POST /#X-Amz-Target=AlexaForBusiness.DeleteDevice
- "Create a #X-Amz-Target=AlexaForBusiness.DeleteDeviceUsageData?" -> POST /#X-Amz-Target=AlexaForBusiness.DeleteDeviceUsageData
- "Create a #X-Amz-Target=AlexaForBusiness.DeleteGatewayGroup?" -> POST /#X-Amz-Target=AlexaForBusiness.DeleteGatewayGroup
- "Create a #X-Amz-Target=AlexaForBusiness.DeleteNetworkProfile?" -> POST /#X-Amz-Target=AlexaForBusiness.DeleteNetworkProfile
- "Create a #X-Amz-Target=AlexaForBusiness.DeleteProfile?" -> POST /#X-Amz-Target=AlexaForBusiness.DeleteProfile
- "Create a #X-Amz-Target=AlexaForBusiness.DeleteRoom?" -> POST /#X-Amz-Target=AlexaForBusiness.DeleteRoom
- "Create a #X-Amz-Target=AlexaForBusiness.DeleteRoomSkillParameter?" -> POST /#X-Amz-Target=AlexaForBusiness.DeleteRoomSkillParameter
- "Create a #X-Amz-Target=AlexaForBusiness.DeleteSkillAuthorization?" -> POST /#X-Amz-Target=AlexaForBusiness.DeleteSkillAuthorization
- "Create a #X-Amz-Target=AlexaForBusiness.DeleteSkillGroup?" -> POST /#X-Amz-Target=AlexaForBusiness.DeleteSkillGroup
- "Create a #X-Amz-Target=AlexaForBusiness.DeleteUser?" -> POST /#X-Amz-Target=AlexaForBusiness.DeleteUser
- "Create a #X-Amz-Target=AlexaForBusiness.DisassociateContactFromAddressBook?" -> POST /#X-Amz-Target=AlexaForBusiness.DisassociateContactFromAddressBook
- "Create a #X-Amz-Target=AlexaForBusiness.DisassociateDeviceFromRoom?" -> POST /#X-Amz-Target=AlexaForBusiness.DisassociateDeviceFromRoom
- "Create a #X-Amz-Target=AlexaForBusiness.DisassociateSkillFromSkillGroup?" -> POST /#X-Amz-Target=AlexaForBusiness.DisassociateSkillFromSkillGroup
- "Create a #X-Amz-Target=AlexaForBusiness.DisassociateSkillFromUser?" -> POST /#X-Amz-Target=AlexaForBusiness.DisassociateSkillFromUsers
- "Create a #X-Amz-Target=AlexaForBusiness.DisassociateSkillGroupFromRoom?" -> POST /#X-Amz-Target=AlexaForBusiness.DisassociateSkillGroupFromRoom
- "Create a #X-Amz-Target=AlexaForBusiness.ForgetSmartHomeAppliance?" -> POST /#X-Amz-Target=AlexaForBusiness.ForgetSmartHomeAppliances
- "Create a #X-Amz-Target=AlexaForBusiness.GetAddressBook?" -> POST /#X-Amz-Target=AlexaForBusiness.GetAddressBook
- "Create a #X-Amz-Target=AlexaForBusiness.GetConferencePreference?" -> POST /#X-Amz-Target=AlexaForBusiness.GetConferencePreference
- "Create a #X-Amz-Target=AlexaForBusiness.GetConferenceProvider?" -> POST /#X-Amz-Target=AlexaForBusiness.GetConferenceProvider
- "Create a #X-Amz-Target=AlexaForBusiness.GetContact?" -> POST /#X-Amz-Target=AlexaForBusiness.GetContact
- "Create a #X-Amz-Target=AlexaForBusiness.GetDevice?" -> POST /#X-Amz-Target=AlexaForBusiness.GetDevice
- "Create a #X-Amz-Target=AlexaForBusiness.GetGateway?" -> POST /#X-Amz-Target=AlexaForBusiness.GetGateway
- "Create a #X-Amz-Target=AlexaForBusiness.GetGatewayGroup?" -> POST /#X-Amz-Target=AlexaForBusiness.GetGatewayGroup
- "Create a #X-Amz-Target=AlexaForBusiness.GetInvitationConfiguration?" -> POST /#X-Amz-Target=AlexaForBusiness.GetInvitationConfiguration
- "Create a #X-Amz-Target=AlexaForBusiness.GetNetworkProfile?" -> POST /#X-Amz-Target=AlexaForBusiness.GetNetworkProfile
- "Create a #X-Amz-Target=AlexaForBusiness.GetProfile?" -> POST /#X-Amz-Target=AlexaForBusiness.GetProfile
- "Create a #X-Amz-Target=AlexaForBusiness.GetRoom?" -> POST /#X-Amz-Target=AlexaForBusiness.GetRoom
- "Create a #X-Amz-Target=AlexaForBusiness.GetRoomSkillParameter?" -> POST /#X-Amz-Target=AlexaForBusiness.GetRoomSkillParameter
- "Create a #X-Amz-Target=AlexaForBusiness.GetSkillGroup?" -> POST /#X-Amz-Target=AlexaForBusiness.GetSkillGroup
- "Create a #X-Amz-Target=AlexaForBusiness.ListBusinessReportSchedule?" -> POST /#X-Amz-Target=AlexaForBusiness.ListBusinessReportSchedules
- "Create a #X-Amz-Target=AlexaForBusiness.ListConferenceProvider?" -> POST /#X-Amz-Target=AlexaForBusiness.ListConferenceProviders
- "Create a #X-Amz-Target=AlexaForBusiness.ListDeviceEvent?" -> POST /#X-Amz-Target=AlexaForBusiness.ListDeviceEvents
- "Create a #X-Amz-Target=AlexaForBusiness.ListGatewayGroup?" -> POST /#X-Amz-Target=AlexaForBusiness.ListGatewayGroups
- "Create a #X-Amz-Target=AlexaForBusiness.ListGateway?" -> POST /#X-Amz-Target=AlexaForBusiness.ListGateways
- "Create a #X-Amz-Target=AlexaForBusiness.ListSkill?" -> POST /#X-Amz-Target=AlexaForBusiness.ListSkills
- "Create a #X-Amz-Target=AlexaForBusiness.ListSkillsStoreCategory?" -> POST /#X-Amz-Target=AlexaForBusiness.ListSkillsStoreCategories
- "Create a #X-Amz-Target=AlexaForBusiness.ListSkillsStoreSkillsByCategory?" -> POST /#X-Amz-Target=AlexaForBusiness.ListSkillsStoreSkillsByCategory
- "Create a #X-Amz-Target=AlexaForBusiness.ListSmartHomeAppliance?" -> POST /#X-Amz-Target=AlexaForBusiness.ListSmartHomeAppliances
- "Create a #X-Amz-Target=AlexaForBusiness.ListTag?" -> POST /#X-Amz-Target=AlexaForBusiness.ListTags
- "Create a #X-Amz-Target=AlexaForBusiness.PutConferencePreference?" -> POST /#X-Amz-Target=AlexaForBusiness.PutConferencePreference
- "Create a #X-Amz-Target=AlexaForBusiness.PutInvitationConfiguration?" -> POST /#X-Amz-Target=AlexaForBusiness.PutInvitationConfiguration
- "Create a #X-Amz-Target=AlexaForBusiness.PutRoomSkillParameter?" -> POST /#X-Amz-Target=AlexaForBusiness.PutRoomSkillParameter
- "Create a #X-Amz-Target=AlexaForBusiness.PutSkillAuthorization?" -> POST /#X-Amz-Target=AlexaForBusiness.PutSkillAuthorization
- "Create a #X-Amz-Target=AlexaForBusiness.RegisterAVSDevice?" -> POST /#X-Amz-Target=AlexaForBusiness.RegisterAVSDevice
- "Create a #X-Amz-Target=AlexaForBusiness.RejectSkill?" -> POST /#X-Amz-Target=AlexaForBusiness.RejectSkill
- "Create a #X-Amz-Target=AlexaForBusiness.ResolveRoom?" -> POST /#X-Amz-Target=AlexaForBusiness.ResolveRoom
- "Create a #X-Amz-Target=AlexaForBusiness.RevokeInvitation?" -> POST /#X-Amz-Target=AlexaForBusiness.RevokeInvitation
- "Create a #X-Amz-Target=AlexaForBusiness.SearchAddressBook?" -> POST /#X-Amz-Target=AlexaForBusiness.SearchAddressBooks
- "Create a #X-Amz-Target=AlexaForBusiness.SearchContact?" -> POST /#X-Amz-Target=AlexaForBusiness.SearchContacts
- "Create a #X-Amz-Target=AlexaForBusiness.SearchDevice?" -> POST /#X-Amz-Target=AlexaForBusiness.SearchDevices
- "Create a #X-Amz-Target=AlexaForBusiness.SearchNetworkProfile?" -> POST /#X-Amz-Target=AlexaForBusiness.SearchNetworkProfiles
- "Create a #X-Amz-Target=AlexaForBusiness.SearchProfile?" -> POST /#X-Amz-Target=AlexaForBusiness.SearchProfiles
- "Create a #X-Amz-Target=AlexaForBusiness.SearchRoom?" -> POST /#X-Amz-Target=AlexaForBusiness.SearchRooms
- "Create a #X-Amz-Target=AlexaForBusiness.SearchSkillGroup?" -> POST /#X-Amz-Target=AlexaForBusiness.SearchSkillGroups
- "Create a #X-Amz-Target=AlexaForBusiness.SearchUser?" -> POST /#X-Amz-Target=AlexaForBusiness.SearchUsers
- "Create a #X-Amz-Target=AlexaForBusiness.SendAnnouncement?" -> POST /#X-Amz-Target=AlexaForBusiness.SendAnnouncement
- "Create a #X-Amz-Target=AlexaForBusiness.SendInvitation?" -> POST /#X-Amz-Target=AlexaForBusiness.SendInvitation
- "Create a #X-Amz-Target=AlexaForBusiness.StartDeviceSync?" -> POST /#X-Amz-Target=AlexaForBusiness.StartDeviceSync
- "Create a #X-Amz-Target=AlexaForBusiness.StartSmartHomeApplianceDiscovery?" -> POST /#X-Amz-Target=AlexaForBusiness.StartSmartHomeApplianceDiscovery
- "Create a #X-Amz-Target=AlexaForBusiness.TagResource?" -> POST /#X-Amz-Target=AlexaForBusiness.TagResource
- "Create a #X-Amz-Target=AlexaForBusiness.UntagResource?" -> POST /#X-Amz-Target=AlexaForBusiness.UntagResource
- "Create a #X-Amz-Target=AlexaForBusiness.UpdateAddressBook?" -> POST /#X-Amz-Target=AlexaForBusiness.UpdateAddressBook
- "Create a #X-Amz-Target=AlexaForBusiness.UpdateBusinessReportSchedule?" -> POST /#X-Amz-Target=AlexaForBusiness.UpdateBusinessReportSchedule
- "Create a #X-Amz-Target=AlexaForBusiness.UpdateConferenceProvider?" -> POST /#X-Amz-Target=AlexaForBusiness.UpdateConferenceProvider
- "Create a #X-Amz-Target=AlexaForBusiness.UpdateContact?" -> POST /#X-Amz-Target=AlexaForBusiness.UpdateContact
- "Create a #X-Amz-Target=AlexaForBusiness.UpdateDevice?" -> POST /#X-Amz-Target=AlexaForBusiness.UpdateDevice
- "Create a #X-Amz-Target=AlexaForBusiness.UpdateGateway?" -> POST /#X-Amz-Target=AlexaForBusiness.UpdateGateway
- "Create a #X-Amz-Target=AlexaForBusiness.UpdateGatewayGroup?" -> POST /#X-Amz-Target=AlexaForBusiness.UpdateGatewayGroup
- "Create a #X-Amz-Target=AlexaForBusiness.UpdateNetworkProfile?" -> POST /#X-Amz-Target=AlexaForBusiness.UpdateNetworkProfile
- "Create a #X-Amz-Target=AlexaForBusiness.UpdateProfile?" -> POST /#X-Amz-Target=AlexaForBusiness.UpdateProfile
- "Create a #X-Amz-Target=AlexaForBusiness.UpdateRoom?" -> POST /#X-Amz-Target=AlexaForBusiness.UpdateRoom
- "Create a #X-Amz-Target=AlexaForBusiness.UpdateSkillGroup?" -> POST /#X-Amz-Target=AlexaForBusiness.UpdateSkillGroup
- "How to authenticate?" -> See Auth section

## Response Tips
- Check response schemas in references/api-spec.lap for field details
- Create/update endpoints typically return the created/updated object

## CLI

```bash
# Update this spec to the latest version
npx @lap-platform/lapsh get alexa-for-business -o references/api-spec.lap

# Search for related APIs
npx @lap-platform/lapsh search alexa-for-business
```

## References
- Full spec: See references/api-spec.lap for complete endpoint details, parameter tables, and response schemas

> Generated from the official API spec by [LAP](https://lap.sh)
