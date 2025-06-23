namespace MG.BLL
{
	public interface IMessage_BLL
	{
		Task<ResponseDTO<Message>> GetMessageByFolderAndId(string email, string folder, string messageId);

		Task<ResponseDTO<Message>> GetMessagebyId(string email, string messageId);

		Task<ResponseDTO<string>> DownloadMessage(string email, string messageId);

		Task<Stream> DownloadMessageasStream(string email, string messageId);

		Task<ResponseDTO<List<Message>>> GetMessagesbyFolder(string email, string folderName, string filter, int pageNumber, int pageSize);

		Task<ResponseDTO<List<FileAttachment>>> GetAttachmentsbyMessageId(string email, string messageId);

		Task<ResponseDTO<FileAttachment>> GetAttachmentbyId(string email, string messageId, string attachmentId);

		Task<byte[]> DownloadAttachmentbyId(string email, string messageId, string attachmentId);

		Task<ResponseDTO<List<MailFolder>>> GetChildFolders(string email, string parentFolderName);

		Task<ResponseDTO<Message>> MoveMessage(string email, string messageId, string destinationFolderId);

		Task<ResponseDTO<Dictionary<string, List<string>>>> GetMessageHeaders(string email, string messageId);
	}
}
