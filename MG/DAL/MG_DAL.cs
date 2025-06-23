namespace MG.DAL
{
	public class MG_DAL : IMG_DAL
	{
		//===============================================================================================================
		// Limiting application permissions to specific Exchange Online mailboxes.
		// https://learn.microsoft.com/en-us/graph/auth-limit-mailbox-access
		// We created an AD group named "AllowAppsToReadADDetails" to control access based on the above article.
		// For accessing more mailboxes, add those mailboxes as members to the above group.
		//===============================================================================================================

		//===============================================================================================================
		// #Powershell code to grant access to managed identity for specified roles
		// #https://www.rahulpnath.com/blog/how-to-authenticate-with-microsoft-graph-api-using-managed-service-identity/
		// cls
		// Connect-AzureAD #-Credential (Get-Credential)
		// $graph = Get-AzureADServicePrincipal -Filter "AppId eq '00000003-0000-0000-c000-000000000000'" #This is the hardcoded ID for graph API. Dont change it.
		// $groupReadPermission = $graph.AppRoles `
		//    | where Value -Like "User.Read.All" ` #This is the role for which we are granting access. Change as needed
		//    | Select-Object -First 1

		// $msi = Get-AzureADServicePrincipal -ObjectId 859d18f3-0b6c-429a-a81b-2eb07046f28e // This is AS-MG-DEV

		// #The below command is for adding. For removing, use Remove-AzureADServiceAppRoleAssignment
		// New-AzureADServiceAppRoleAssignment `
		//    -Id $groupReadPermission.Id `
		//    -ObjectId $msi.ObjectId `
		//    -PrincipalId $msi.ObjectId `
		//    -ResourceId $graph.ObjectId
		//===============================================================================================================

		//===============================================================================================================
		// Powershell code to grant access to managed identity for specific Sharepoint sites when using the role "Sites.Selected"
		// The below code gives access to the whole site and not the individual Lists/Libraries. TODO: Figure out how to give access to individual Lists/Libraries
		// Need to install powershell 7 to run these commands
		//cls
		//Import-Module PnP.PowerShell

		//# Provide the URL of the SharePoint Online site you want to connect to
		//$siteUrl = "https://liscr.sharepoint.com/"

		//# Connect to the SharePoint Online site using Connect-PnPOnline
		//Connect-PnPOnline -Url $siteUrl -Interactive

		//# Command to read exisitng permissions on the site
		//#Get-PnPAzureADAppSitePermission -AppIdentity <String> [-Site <SitePipeBind>] [-Connection <PnPConnection>]
		//Get-PnPAzureADAppSitePermission -Site $siteUrl

		//# Command to grant permissions
		//#Grant-PnPAzureADAppSitePermission -AppId <Guid> -DisplayName <String> -Permissions <Read|Write> [-Site <SitePipeBind>] [-Connection <PnPConnection>]
		//#Grant-PnPAzureADAppSitePermission -AppId 'c5e23222-6ceb-4e2d-8b27-d85f7fcbad83' -DisplayName 'AS-MG-TST' -Site $siteUrl -Permissions Write

		//# Command to set permission once its granted. This should be used if you want to modify the permissions after they have been granted
		//#Set-PnPAzureADAppSitePermission -PermissionId <String> -Permissions <Read|Write|Manage|FullControl> [-Site <SitePipeBind>] [-Connection <PnPConnection>]

		//# Command to revoke permission
		//#Revoke-PnPAzureADAppSitePermission -PermissionId <String> [-Site <SitePipeBind>] [-Connection <PnPConnection>]
		//===============================================================================================================

		private readonly Config _config;
		private readonly GraphServiceClient graphServiceClient;

		public MG_DAL(IOptions<Config> config)
		{
			_config = config.Value;

			var tenantId = _config.TenantId;
			var clientId = _config.ClientId;
			var clientSecret = _config.ClientSecret;
			var scopes = new[] { "https://graph.microsoft.com/.default" };

#if DEBUG
			IConfidentialClientApplication app = ConfidentialClientApplicationBuilder
				.Create(clientId)
				.WithClientSecret(clientSecret)
				.WithAuthority(new Uri($"https://login.microsoftonline.com/{tenantId}"))
				.Build();

			var clientSecretCredential = new ClientSecretCredential(tenantId, clientId, clientSecret);

			graphServiceClient = new GraphServiceClient(clientSecretCredential, scopes);
#else
			var tokenCredential = new ManagedIdentityCredential();
			graphServiceClient = new GraphServiceClient(tokenCredential, scopes);
#endif
		}

		#region Calendar
		// TODO: ViewModel should not be passed to DAL. ViewModel (CalendarEventViewModel) to DataModel (Event) should be mapped in BLL
		public async Task<dynamic> CreateCalendarEvent(CalendarEventViewModel calendar)
		{
			EmailClass emailClass = new EmailClass();
			var emailBody = emailClass.FrameEmailBody(calendar.startDatetime, calendar.MeetingLink, calendar.timeZone);
			var endTime = Convert.ToDateTime(calendar.startDatetime).AddHours(1);
			return await graphServiceClient.Users["ConnectNowDev@liscr.com"].Events
				.PostAsync(new Event
				{
					Subject = $"Connect.Now :{calendar.MeetingLink}",
					Body = new ItemBody
					{
						ContentType = BodyType.Html,
						Content = emailBody
					},
					Start = new DateTimeTimeZone
					{
						DateTime = calendar.startDatetime,//"2020-05-09T15:00:00",
						TimeZone = calendar.timeZone
					},
					End = new DateTimeTimeZone
					{
						DateTime = Convert.ToString(endTime),//"2020-05-09T16:00:00",
						TimeZone = calendar.timeZone
					},
					//Location = new Location
					//{
					//	DisplayName = calendar.location
					//},
					Attendees = new List<Attendee>()
									{
										new Attendee
										{
											EmailAddress = new EmailAddress
											{
												Address = calendar.attendeeEmail,
												Name = calendar.attendeeDisplayName?? ""
											},
											Type = AttendeeType.Required
										},
										new Attendee
										{
											EmailAddress = new EmailAddress
											{
												Address = calendar.dutyOfficerEmail,
												Name = calendar.dutyOfficerDisplayName?? ""
											},
											Type = AttendeeType.Required
										}
									}
				});
		}
		#endregion Calendar

		#region Mail
		public async Task<Message> GetMessageByFolderAndId(string email, string folder, string messageId)
		{
			return await graphServiceClient.Users[email].MailFolders[folder].Messages[messageId].GetAsync();
		}

		public async Task<Message> GetMessagebyId(string email, string messageId)
		{
			return await graphServiceClient.Users[email].Messages[messageId].GetAsync();
		}

		public async Task<Dictionary<string, List<string>>> GetMessageHeaders(string email, string messageId)
		{
			var message = await graphServiceClient.Users[email].Messages[messageId].GetAsync(config =>
			{
				config.QueryParameters.Select = ["internetMessageHeaders"];
			});

			if (message.InternetMessageHeaders == null || !message.InternetMessageHeaders.Any())
			{
				return new Dictionary<string, List<string>>();
			}
			return message.InternetMessageHeaders.GroupBy(h => h.Name).ToDictionary(g => g.Key, g => g.Select(h => h.Value).ToList());
		}


		public async Task<Stream> DownloadMessage(string email, string messageId)
		{
			return await graphServiceClient.Users[email].Messages[messageId].Content.GetAsync();
		}

		public async Task<List<Message>> GetMessagesbyFolder(string email, string folderName, int pageNumber, int pageSize, MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters options)
		{
			List<Message> returnValue = new List<Message>();

			var response = await graphServiceClient
								.Users[email]
								.MailFolders[folderName]
								.Messages
								.GetAsync(reqConfig =>
								{
									reqConfig.QueryParameters.Top = pageSize;
									reqConfig.QueryParameters.Skip = (pageNumber - 1) * pageSize;
									reqConfig.QueryParameters.Filter = options.Filter;
									reqConfig.QueryParameters.Search = options.Search;
									reqConfig.QueryParameters.Select = options.Select;
									reqConfig.Headers.Add("Prefer", "HonorNonIndexedQueriesWarningMayFailRandomly");
								});

			if (response != null)
			{
				await GetPageIterator(returnValue, response, pageSize).IterateAsync();
			}

			return returnValue;
		}

		public async Task<List<Attachment>> GetAttachmentsbyMessageId(string email, string messageId, int count)
		{
			List<Attachment> returnValue = new List<Attachment>();

			var response = await graphServiceClient.Users[email].Messages[messageId].Attachments.GetAsync();

			if (response == null)
			{
				return returnValue;
			}

			await GetPageIterator(returnValue, response, count).IterateAsync();

			return returnValue;
		}

		public async Task<Attachment> GetAttachmentbyId(string email, string messageId, string attachmentId)
		{
			return await graphServiceClient.Users[email].Messages[messageId].Attachments[attachmentId].GetAsync(requestConfig =>
			{
				requestConfig.QueryParameters.Select = new[] { "id", "name", "size", "contentType", "isInline", "lastModifiedDateTime" };
			});
		}

		public async Task<byte[]> DownloadAttachmentbyId(string email, string messageId, string attachmentId)
		{
			var attachment = await graphServiceClient.Users[email].Messages[messageId].Attachments[attachmentId].GetAsync();
			return (attachment as FileAttachment).ContentBytes;
		}

		public async Task<List<MailFolder>> GetChildFolders(string email, string parentFolderName)
		{
			List<MailFolder> returnValue = new List<MailFolder>();
			var response = await graphServiceClient.Users[email].MailFolders[parentFolderName].ChildFolders.GetAsync();
			if (response == null)
			{
				return returnValue;
			}

			await GetPageIterator(returnValue, response, 100).IterateAsync();

			return returnValue;
		}

		public async Task<Message> MoveMessage(string email, string messageId, string destinationFolderId)
		{
			return await graphServiceClient.Users[email].Messages[messageId].Move
					.PostAsync(new Microsoft.Graph.Users.Item.Messages.Item.Move.MovePostRequestBody
					{
						DestinationId = destinationFolderId
					});
		}
		#endregion

		#region SharePoint
		//public async Task<Site> GetRootSiteDetails()
		//{
		//	return await graphServiceClient.Sites.GetAllSites.GetAsync();
		//}

		public async Task<List<List>> GetSiteLists(string siteId)
		{
			var response = await graphServiceClient.Sites[siteId].Lists.GetAsync();

			return response.Value;
		}

		public async Task<List> GetListDetails(string siteId, string listId)
		{
			return await graphServiceClient.Sites[siteId].Lists[listId].GetAsync();
		}

		public async Task<List<ListItem>> GetListItems(string siteId, string listId, int pageSize, ItemsRequestBuilder.ItemsRequestBuilderGetQueryParameters requestConfiguration)
		{
			List<ListItem> returnValue = new List<ListItem>();

			var response = await graphServiceClient.Sites[siteId].Lists[listId].Items
								.GetAsync(reqConfig =>
								{
									if (!string.IsNullOrEmpty(requestConfiguration.Filter))
									{
										reqConfig.QueryParameters.Filter = requestConfiguration.Filter;
									}

									if (!string.IsNullOrEmpty(requestConfiguration.Search))
									{
										reqConfig.QueryParameters.Search = requestConfiguration.Search;
									}

									if (requestConfiguration.Expand != null && requestConfiguration.Expand.Length != 0)
									{
										reqConfig.QueryParameters.Expand = requestConfiguration.Expand;
									}

									if (pageSize < 200)
									{
										reqConfig.QueryParameters.Top = pageSize;
									}

									reqConfig.Headers.Add("Prefer", "HonorNonIndexedQueriesWarningMayFailRandomly");
								});

			if (response == null)
			{
				return returnValue;
			}

			await GetPageIterator(returnValue, response, pageSize).IterateAsync();

			return returnValue;
		}

		public async Task<Stream> DownloadFile(string siteId, string listId, string itemId)
		{
			var response = await graphServiceClient.Sites[siteId].Lists[listId].Items[itemId]
								.GetAsync((reqConfig) =>
								{
									reqConfig.QueryParameters.Expand = new[] { "driveItem($select=id,name,webUrl)" };
								});

			var driveItemId = response.DriveItem.Id;

			var driveInfo = await graphServiceClient.Sites[siteId].Drive
								.GetAsync((reqConfig) =>
								{
									reqConfig.Headers.Add("Prefer", "allowthrottleablequeries");
								});

			var driveId = driveInfo.Id;

			return await graphServiceClient.Drives[driveId].Items[driveItemId].Content.GetAsync();

		}

		public async Task<List<string>> AddListItems(string siteId, string listId, List<Dictionary<string, object>> items)
		{
			List<string> response = new List<string>();

			var batchCollection = new BatchRequestContentCollection(graphServiceClient);

			foreach (var entryitem in items)
			{
				var item = new ListItem
				{
					Fields = new FieldValueSet
					{
						AdditionalData = entryitem
					}
				};

				await batchCollection.AddBatchRequestStepAsync(graphServiceClient.Sites[siteId].Lists[listId].Items.ToPostRequestInformation(item));
			}

			var batchResponseContentCollection = await graphServiceClient.Batch.PostAsync(batchCollection);

			var responseStatus = batchResponseContentCollection.GetResponsesStatusCodesAsync();

			return response;
		}

		public async Task<List<string>> UpdateListItems(string siteId, string listId, List<Dictionary<string, object>> items)
		{
			List<string> response = new List<string>();

			var batchCollection = new BatchRequestContentCollection(graphServiceClient);

			foreach (var entryitem in items)
			{
				var listitemid = entryitem["id"].ToString();

				entryitem.Remove("id");

				var item = new ListItem
				{
					Fields = new FieldValueSet
					{
						AdditionalData = entryitem
					}
				};

				if (!string.IsNullOrEmpty(listitemid))
				{
					var res = await batchCollection.AddBatchRequestStepAsync(graphServiceClient.Sites[siteId].Lists[listId].Items[listitemid].Fields.ToPatchRequestInformation(item.Fields));

					if (!string.IsNullOrEmpty(res))
						response.Add(res);
				}
			}

			var batchResponseContentCollection = await graphServiceClient.Batch.PostAsync(batchCollection);

			return response;
		}

		public async Task DeleteListItems(string siteId, string listId, int pageSize, ItemsRequestBuilder.ItemsRequestBuilderGetQueryParameters requestConfiguration)
		{
			var items = await GetListItems(siteId, listId, pageSize, requestConfiguration);

			var batchCollection = new BatchRequestContentCollection(graphServiceClient);

			foreach (var item in items)
			{
				var deleteItemRequest = graphServiceClient.Sites[siteId].Lists[listId].Items[item.Id].ToDeleteRequestInformation();

				await batchCollection.AddBatchRequestStepAsync(deleteItemRequest);
			}

			await graphServiceClient.Batch.PostAsync(batchCollection);
		}

		public async Task<dynamic> SearchListItems(List<SearchRequest> searchModel)
		{
			var reqBody = new QueryPostRequestBody
			{
				Requests = searchModel
			};

			var response = await graphServiceClient.Search.Query.PostAsQueryPostResponseAsync(reqBody, null);

			if (response == null)
			{
				return null;
			}

			if (response.Value.FirstOrDefault()?.HitsContainers.FirstOrDefault().Total > 0)
			{
				return await GetSerializedContent(response);
			}
			else
			{
				return null;
			}
		}

		#endregion SharePoint

		#region Teams
		public async Task<List<Group>> GetAllTeams(string searchString)
		{
			List<Group> returnValue = new List<Group>();

			var response = await graphServiceClient.Groups
								.GetAsync(reqConfig =>
								{
									reqConfig.QueryParameters.Filter = $"startswith(displayName,'{searchString}') and resourceProvisioningOptions/Any(x:x eq 'Team')";
								});

			if (response == null)
			{
				return returnValue;
			}

			await GetPageIterator(returnValue, response).IterateAsync();

			return returnValue;
		}

		public async Task<Group> GetTeambyId(string id)
		{
			return await graphServiceClient.Groups[id].GetAsync();
		}

		public async Task<Group> GetTeambyName(string displayName)
		{
			List<Group> returnValue = new List<Group>();

			var response = await graphServiceClient.Groups
								.GetAsync(reqConfig =>
								{
									reqConfig.QueryParameters.Filter = $"displayName eq '{displayName}'";
								});

			if (response == null)
			{
				return null;
			}

			await GetPageIterator(returnValue, response).IterateAsync();

			return returnValue.FirstOrDefault();

		}

		public async Task<List<Channel>> GetTeamChannels(string id)
		{
			List<Channel> returnValue = new List<Channel>();
			var response = await graphServiceClient.Teams[id].Channels.GetAsync();

			if (response == null)
			{
				return null;
			}

			await GetPageIterator(returnValue, response).IterateAsync();

			return returnValue;
		}

		public async Task SendMessagetoUser(string userEmail, string body)
		{
			throw new NotImplementedException();
		}
		#endregion Teams

		#region Users
		public async Task<User> GetUserbyEmail(string email)
		{
			return await graphServiceClient.Users[email].GetAsync();
		}

		public async Task<byte[]> GetProfilePicturebyEmail(string email)
		{
			var response = await graphServiceClient.Users[email].Photo.Content.GetAsync();
			if (response != null)
			{
				MemoryStream ms = new MemoryStream();
				response.CopyTo(ms);
				return ms.ToArray();
			}
			else
			{
				return null;
			}
		}

		public async Task<User> GetUsersManagerbyEmail(string email)
		{
			return (User)await graphServiceClient.Users[email].Manager.GetAsync();
		}

		//public async Task<User> UpdateUser(User user)
		//{
		//	return await graphServiceClient.Users[user.UserPrincipalName].Request().UpdateAsync(user);
		//}

		//public async Task UpdateUserManager(User user, User manager)
		//{
		//	var requestBody = new ReferenceUpdate
		//	{
		//		OdataId = $"https://graph.microsoft.com/v1.0/users/{manager.Id}"
		//	};
		//	await graphServiceClient.Users[user.UserPrincipalName].Manager.Ref.PutAsync(requestBody);
		//}
		#endregion Users

		private async Task<string> GetSerializedContent(QueryPostResponse response)
		{
			using (var serializer = new JsonSerializationWriter())
			{
				serializer.WriteObjectValue(string.Empty, response);

				using (StreamReader sr = new StreamReader(serializer.GetSerializedContent()))
				{
					return await sr.ReadToEndAsync();
				}
			}
		}

		private PageIterator<TEntity, TCollectionPage> GetPageIterator<TEntity, TCollectionPage>(List<TEntity> returnValue, TCollectionPage response, int reponseSize = 10) where TCollectionPage : IParsable, IAdditionalDataHolder, new()
		{
			return PageIterator<TEntity, TCollectionPage>.CreatePageIterator(
															graphServiceClient,
															response,
															// Callback executed for each item in the collection
															(item) =>
															{
																returnValue.Add(item);
																return returnValue.Count < reponseSize;
															},
															// Used to configure subsequent page requests
															(requestInfo) =>
															{
																// Re-add the header to subsequent requests
																requestInfo.Headers.Add("Prefer", "HonorNonIndexedQueriesWarningMayFailRandomly");
																return requestInfo;
															});
		}
	}

	public class EmailClass
	{
		public string FrameEmailBody(string scheduleMeetingTime, string MeetingLink, string TimeZone)
		{
			string EmailBody = string.Empty;
			EmailBody += "<div style='max-width: 720px;height: auto;border: 1px solid #fff;overflow: auto;background: #fff;'>";
			EmailBody += "<div style='height: 74px;background: #fff;padding: 21px 0px;text-align: left;max-width: 720px;'>";
			EmailBody += "<img src='https://saappsdevenv.blob.core.windows.net/marketing/Connect-Now-Logo' alt='The Liberian Registry' style ='image-rendering: -webkit-optimize-contrast; padding: 3px;height: 84px;'/></div>";
			EmailBody += "<div style='width:99%; height:100px; padding-top: 64px; margin-top:0px; margin-bottom:0px; border:1px solid #e9e9e9; background: #074a53; color: #fff; text-align: left; padding-bottom: 30px;'>";
			EmailBody += "<div style='text-align: left; font-size: 24pt; font-weight: 600; font-family: sans-serif;padding-left: 30px;'>Connect.Now Meeting</div>";
			EmailBody += $"<div style ='text-align: left; font-size: 16px; margin-top: 8px; font-family: sans-serif; color: #ffffff;padding-left: 30px;' >{scheduleMeetingTime} ({TimeZone})</div></div>";
			EmailBody += "<div style = 'width: 95%;height: 49px;margin-left: auto;margin-right: auto;font-size: 14px;font-family: sans-serif;background: #fff;padding-top: 27px;text-align: left;color: #444;padding-left: 30px;'>Your meeting with duty officer is confirmed! Click below to join at the scheduled time.</div> ";
			EmailBody += $"<div style='width: 100%; margin-left: auto; margin-right: auto; margin-top: 0px; text-align: left; margin-bottom: 0px; background: #fff; height: 57px; border-top: 1px solid #f5f5f5; padding-top: 40px;'><a href='http://dev.liscr.com?meetingId={MeetingLink}' style='padding: 18px 40px;background: #074a53;color: #fff;font-family: sans-serif;font-size: 16px;font-weight: 700;height: 122px;margin-left: 27px;border-radius: 0px;box-shadow: 1px 4px 10px 1px #ccc;border: 0px solid #fff;'>JOIN MEETING</a></div>";
			EmailBody += "<div style = 'width: 97%;margin-left: auto;margin-right: auto;background: #fff;border-top: 1px solid #f5f5f5;padding: 5px 8px;/* box-shadow: 9px 16px 13px 1px #d9d9d9; */margin-bottom: 90px;'>";

			EmailBody += "<div style='font-family: sans-serif;font-weight: 500;font-size: 16px;padding: 0px 22px;height: 24px;margin-top: 23px;font-style: italic;'>Thank you,</div>";
			EmailBody += "<div style='font-family: sans-serif;font-weight: bold;font-size: 14px;padding: 1px 25px;margin-bottom: 36px;color: #818181;'>LISCR</div> </div>";
			EmailBody += "<div style='width: 100%; height: 45px; background: #fff; text-align: center;'> <div style='padding: 12px; color: #a5a5a5; font-family: system-ui; font-size: 12px;'> Copyright © 2016 - 2022 LISCR.All rights reserved.</div></div></div>";
			return EmailBody;
		}
	}
}
