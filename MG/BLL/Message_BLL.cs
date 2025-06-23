namespace MG.BLL
{
	public class Message_BLL : IMessage_BLL
	{
		IMG_DAL _mgDAL;
		ILogger<Message_BLL> _logger;

		public Message_BLL(ILogger<Message_BLL> logger, IMG_DAL mgDAL)
		{
			_logger = logger;
			_mgDAL = mgDAL;
		}

		public async Task<ResponseDTO<Message>> GetMessageByFolderAndId(string email, string folder, string messageId)
		{
			try
			{
				var message = await _mgDAL.GetMessageByFolderAndId(email, folder, messageId);
				return new ResponseDTO<Message> { Data = message, Success = true };
			}
			catch (Exception ex)
			{
				return new ResponseDTO<Message> { Success = false, ErrorMessage = ex.Message };
			}
		}

		public async Task<ResponseDTO<Message>> GetMessagebyId(string email, string messageId)
		{
			try
			{
				var message = await _mgDAL.GetMessagebyId(email, messageId);
				return new ResponseDTO<Message> { Data = message, Success = true };
			}
			catch (Exception ex)
			{
				return new ResponseDTO<Message> { Success = false, ErrorMessage = ex.Message };
			}
		}

		public async Task<ResponseDTO<Dictionary<string, List<string>>>> GetMessageHeaders(string email, string messageId)
		{
			try
			{
				var headers = await _mgDAL.GetMessageHeaders(email, messageId);
				return new ResponseDTO<Dictionary<string, List<string>>> { Data = headers, Success = true };
			}
			catch (Exception ex)
			{
				return new ResponseDTO<Dictionary<string, List<string>>> { Success = false, ErrorMessage = ex.Message };
			}
		}

		public async Task<ResponseDTO<string>> DownloadMessage(string email, string messageId)
		{
			try
			{
				var message = await _mgDAL.DownloadMessage(email, messageId);
				StreamReader reader = new StreamReader(message); // TODO Need to properly dispose of the stream
				return new ResponseDTO<string> { Data = reader.ReadToEnd(), Success = true };
			}
			catch (Exception ex)
			{
				return new ResponseDTO<string> { Success = false, ErrorMessage = ex.Message };
			}
		}

		public async Task<Stream> DownloadMessageasStream(string email, string messageId)
		{
			try
			{
				return await _mgDAL.DownloadMessage(email, messageId);
			}
			catch (Exception ex)
			{
				_logger.LogError(ex, $"Error downloading message for messageId {messageId}");
				return null;
			}
		}

		public async Task<ResponseDTO<List<Message>>> GetMessagesbyFolder(string email, string folderName, string filter, int pageNumber, int pageSize)
		{
			try
			{
				var options = new MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters()
				{
					Filter = filter,
					Orderby = new string[] { "receivedDateTime asc" }
				};

				var messages = await _mgDAL.GetMessagesbyFolder(email, folderName, pageNumber, pageSize, options);
				return new ResponseDTO<List<Message>> { Data = messages, Success = true };
			}
			catch (Exception ex)
			{
				return new ResponseDTO<List<Message>> { Success = false, ErrorMessage = ex.Message };
			}
		}

		public async Task<ResponseDTO<List<FileAttachment>>> GetAttachmentsbyMessageId(string email, string messageId)
		{
			try
			{
				var messages = await _mgDAL.GetAttachmentsbyMessageId(email, messageId, 100);
				return new ResponseDTO<List<FileAttachment>>
				{
					Data = messages.Where(w => w is FileAttachment).Select(s => s as FileAttachment).Select(s => new FileAttachment
					{
						ContentId = s.ContentId,
						ContentType = s.ContentType,
						Id = s.Id,
						IsInline = s.IsInline,
						LastModifiedDateTime = s.LastModifiedDateTime,
						Name = s.Name,
						Size = s.Size
					}).ToList(),
					Success = true
				};
			}
			catch (Exception ex)
			{
				return new ResponseDTO<List<FileAttachment>> { Success = false, ErrorMessage = ex.Message };
			}
		}

		public async Task<ResponseDTO<FileAttachment>> GetAttachmentbyId(string email, string messageId, string attachmentId)
		{
			try
			{
				var messages = await _mgDAL.GetAttachmentbyId(email, messageId, attachmentId);
				return new ResponseDTO<FileAttachment> { Data = messages as FileAttachment, Success = true };
			}
			catch (Exception ex)
			{
				return new ResponseDTO<FileAttachment> { Success = false, ErrorMessage = ex.Message };
			}
		}

		public async Task<byte[]> DownloadAttachmentbyId(string email, string messageId, string attachmentId)
		{
			try
			{
				return await _mgDAL.DownloadAttachmentbyId(email, messageId, attachmentId);
			}
			catch (Exception ex)
			{
				_logger.LogError(ex, $"Error downloading attachment for messageId {messageId} and attachmentId {attachmentId}");
				return null;
			}
		}

		public async Task<ResponseDTO<List<MailFolder>>> GetChildFolders(string email, string parentFolderName)
		{
			try
			{
				var messages = await _mgDAL.GetChildFolders(email, parentFolderName);
				return new ResponseDTO<List<MailFolder>> { Data = messages, Success = true };
			}
			catch (Exception ex)
			{
				return new ResponseDTO<List<MailFolder>> { Success = false, ErrorMessage = ex.Message };
			}
		}

		public async Task<ResponseDTO<Message>> MoveMessage(string email, string messageId, string destinationFolderId)
		{
			try
			{
				var messages = await _mgDAL.MoveMessage(email, messageId, destinationFolderId);
				return new ResponseDTO<Message> { Data = messages, Success = true };
			}
			catch (Exception ex)
			{
				return new ResponseDTO<Message> { Success = false, ErrorMessage = ex.Message };
			}
		}
	}
}
