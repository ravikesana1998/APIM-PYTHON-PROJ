namespace MG.BLL
{
	public interface ISharePoint_BLL
	{
		
		Task<ResponseDTO<byte[]>> DownloadFile(string siteId, string listId, string itemId);

		Task<ResponseDTO<List<List>>> GetSiteLists(string siteId);

		Task<ResponseDTO<List>> GetListDetails(string siteId, string listId);

		Task<ResponseDTO<dynamic>> GetListItems(GetSharePointModel sharepointModel);

		Task<ResponseDTO<List<string>>> AddListItems(AddSharePointModel sharePointModel);

		Task<ResponseDTO<List<string>>> UpdateListItems(AddSharePointModel sharePointModel);

		Task<ResponseDTO<bool>> DeleteListItems(GetSharePointModel sharepointModel);
		Task<ResponseDTO<dynamic>> SearchListItems(SearchSharePointModel searchModel);
	}
}
