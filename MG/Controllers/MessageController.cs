namespace MG.Controllers
{
	public class MessageController : BaseController
	{

		public MessageController(IMessage_BLL mailBll)
		{
			_mailBll = mailBll;
		}

		[HttpGet("{email}/{folder}/{messageId}")]
		public async Task<ActionResult> GetMessageByFolderAndId(string email, string folder, string messageId)
		{
			var response = await _mailBll.GetMessageByFolderAndId(email, folder, messageId);
			return Ok(response);
		}

		[HttpGet("{email}/{messageId}")]
		public async Task<ActionResult> GetMessagebyId(string email, string messageId)
		{
			var response = await _mailBll.GetMessagebyId(email, messageId);
			return Ok(response);
		}

		[HttpGet("{email}/{messageId}")]
		public async Task<ActionResult> GetMessageHeaders(string email, string messageId)
		{
			var response = await _mailBll.GetMessageHeaders(email, messageId);
			return Ok(response);
		}

		[HttpGet("{email}/{messageId}")]
		public async Task<ActionResult> DownloadMessage(string email, string messageId)
		{
			var response = await _mailBll.DownloadMessage(email, messageId);
			return Ok(response);
		}

		[HttpGet("{email}/{messageId}")]
		public async Task<ActionResult> DownloadMessageasStream(string email, string messageId)
		{
			var response = await _mailBll.DownloadMessageasStream(email, messageId);
			return File(response, "message/rfc822", $"{messageId}.eml");
		}

		[HttpGet("{email}/{folderName}")]
		public async Task<ActionResult> GetMessagesbyFolder(string email, string folderName, string? filter, int pageNumber = 1, int pageSize = 10)
		{
			var response = await _mailBll.GetMessagesbyFolder(email, folderName, filter, pageNumber, pageSize);
			return Ok(response);
		}

		[HttpGet("{email}/{messageId}")]
		public async Task<ActionResult> GetAttachmentsbyMessageId(string email, string messageId)
		{
			var response = await _mailBll.GetAttachmentsbyMessageId(email, messageId);
			return Ok(response);
		}

		[HttpGet("{email}/{messageId}/{attachmentId}")]
		public async Task<ActionResult> DownloadAttachmentbyId(string email, string messageId, string attachmentId)
		{
			var attachment = await _mailBll.GetAttachmentbyId(email, messageId, attachmentId);
			if (attachment.Success && attachment.Data != null)
			{
				var response = await _mailBll.DownloadAttachmentbyId(email, messageId, attachmentId);
				return File(response, attachment.Data.ContentType, attachment.Data.Name);
			}
			else
			{
				return NotFound($"Attachment with name not found in {email} for {messageId}");
			}
		}

		[HttpGet("{email}/{parentFolderName}")]
		public async Task<ActionResult> GetChildFolders(string email, string parentFolderName)
		{
			var response = await _mailBll.GetChildFolders(email, parentFolderName);
			return Ok(response);
		}

		[HttpPost]
		public async Task<ActionResult> MoveMessage(string email, string messageId, string destinationFolderId)
		{
			var response = await _mailBll.MoveMessage(email, messageId, destinationFolderId);
			return Ok(response);
		}
	}
}
