using MG.Models.ViewModels;

namespace MG.Controllers
{
	public class SharePointController : BaseController
	{
		ISharePoint_BLL _spBll;
		public SharePointController(ISharePoint_BLL spBll)
		{
			_spBll = spBll;
		}


		[HttpGet]
		public async Task<ActionResult> GetSiteLists(string siteId)
		{
			var response = await _spBll.GetSiteLists(siteId);
			return Ok(response);
		}

		[HttpGet]
		public async Task<ActionResult> GetListDetails(string siteId, string listId)
		{
			var response = await _spBll.GetListDetails(siteId, listId);
			return Ok(response);
		}

		[HttpPost]
		public async Task<ActionResult> GetListItems(GetSharePointModel sharepointModel)
		{
			var response = await _spBll.GetListItems(sharepointModel);
			return Ok(response);
		}

		[HttpPost]
		public async Task<ActionResult> AddListItems(AddSharePointModel sharePointModel)
		{
			var response = await _spBll.AddListItems(sharePointModel);
			return Ok(response);
		}

		[HttpPost]
		public async Task<ActionResult> UpdateListItems(AddSharePointModel sharePointModel)
		{
			var response = await _spBll.UpdateListItems(sharePointModel);
			return Ok(response);
		}

		[HttpPost]
		public async Task<ActionResult> DeleteListItems(GetSharePointModel SharepointModel)
		{
			var response = await _spBll.DeleteListItems(SharepointModel);
			return Ok(response);
		}

		[HttpGet]
		public async Task<ActionResult> DownloadFile(string siteId, string listId, string itemId)
		{
			var response = await _spBll.DownloadFile(siteId, listId, itemId);

			return Ok(response);
		}

		[HttpPost]
		public async Task<ActionResult> SearchListItems(SearchSharePointModel searchModel)
		{
			var response = await _spBll.SearchListItems(searchModel);
			
			return Ok(response);
		}
	}
}
