namespace MG.DAL
{
	public interface IMG_DAL
	{
		#region Mail
		Task<Message> GetMessageByFolderAndId(string email, string folder, string messageId);

		Task<Message> GetMessagebyId(string email, string messageId);

		Task<Stream> DownloadMessage(string email, string messageId);

		Task<List<Message>> GetMessagesbyFolder(string email, string folderName, int pageNumber, int pageSize, MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters options);

		Task<List<Attachment>> GetAttachmentsbyMessageId(string email, string messageId, int count);

		Task<Attachment> GetAttachmentbyId(string email, string messageId, string attachmentId);

		Task<byte[]> DownloadAttachmentbyId(string email, string messageId, string attachmentId);

		Task<List<MailFolder>> GetChildFolders(string email, string parentFolderName);

		Task<Message> MoveMessage(string email, string messageId, string destinationFolderId);

		Task<Dictionary<string, List<string>>> GetMessageHeaders(string email, string messageId);
		#endregion

		#region SharePoint

		Task<List<List>> GetSiteLists(string siteId);

		Task<List> GetListDetails(string siteId, string listId);

		Task<dynamic> SearchListItems(List<SearchRequest> searchModel);

		Task<List<ListItem>> GetListItems(string siteId, string listId, int pageSize, ItemsRequestBuilder.ItemsRequestBuilderGetQueryParameters requestConfiguration);

		Task<List<string>> AddListItems(string siteId, string listId, List<Dictionary<string, object>> items);

		Task<List<string>> UpdateListItems(string siteId, string listId, List<Dictionary<string, object>> items);

		Task DeleteListItems(string siteId, string listId, int pageSize, ItemsRequestBuilder.ItemsRequestBuilderGetQueryParameters requestConfiguration);

		Task<Stream> DownloadFile(string siteId, string listId, string itemId);

		#endregion SharePoint

		#region Teams
		Task<List<Group>> GetAllTeams(string searchString);
		Task<Group> GetTeambyId(string id);
		Task<Group> GetTeambyName(string displayName);
		Task<List<Channel>> GetTeamChannels(string id);
		Task SendMessagetoUser(string userEmail, string body);
		#endregion Teams

		#region Users
		Task<User> GetUserbyEmail(string email);
		Task<byte[]> GetProfilePicturebyEmail(string email);
		Task<User> GetUsersManagerbyEmail(string email);
		//Task<User> UpdateUser(User user);
		//Task UpdateUserManager(User user, User manager);
		#endregion Users

		Task<dynamic> CreateCalendarEvent(CalendarEventViewModel calendar);
	}
}
