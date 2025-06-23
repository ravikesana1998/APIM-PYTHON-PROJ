namespace MG.Models.ViewModels
{
	public class SharePointBaseModel
	{
		public string SiteId { get; set; }
		public string ListId { get; set; }
	}

	public class SharePointFilterModel
	{
		public string Key { get; set; }
		public string Value { get; set; }
		public string Type { get; set; }
	}

	public class SharePointSearchModel
	{
		public string SearchString { get; set; }
		public string SearchPath { get; set; }
		public List<string> Fields { get; set; }
		public int From { get; set; } = 0;
		public int Size { get; set; } = 25;
	}

	public class GetSharePointModel : SharePointBaseModel
	{
		public List<SharePointFilterModel> SharePointFilterModels { get; set; }
		public List<string> Fields { get; set; } = new List<string>();
		public int RecordCount { get; set; } = 1;
	}
	public class AddSharePointModel : SharePointBaseModel
	{
		public List<Dictionary<string, object>> Items { get; set; }
	}

	public class SearchSharePointModel : SharePointBaseModel
	{
		public SharePointSearchModel searchModels { get; set; }
	}
}
