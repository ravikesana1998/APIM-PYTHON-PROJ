namespace MG.BLL
{
	public class SharePoint_BLL : ISharePoint_BLL
	{
		IMG_DAL _mgDAL;

		public SharePoint_BLL(IMG_DAL mgDAL)
		{
			_mgDAL = mgDAL;
		}

		//public async Task<ResponseDTO<Site>> GetRootSiteDetails()
		//{
		//	try
		//	{
		//		var data = await _mgDAL.GetRootSiteDetails();
		//		return new ResponseDTO<Site> { Data = data, Success = true };
		//	}
		//	catch (Exception ex)
		//	{
		//		return new ResponseDTO<Site> { Success = false, ErrorMessage = ex.Message };
		//	}
		//}

		public async Task<ResponseDTO<List<List>>> GetSiteLists(string siteId)
		{
			try
			{
				var data = await _mgDAL.GetSiteLists(siteId);
				return new ResponseDTO<List<List>> { Data = data, Success = true };
			}
			catch (Exception ex)
			{
				return new ResponseDTO<List<List>> { Success = false, ErrorMessage = ex.Message };
			}
		}

		public async Task<ResponseDTO<List>> GetListDetails(string siteId, string listId)
		{
			try
			{
				var data = await _mgDAL.GetListDetails(siteId, listId);
				return new ResponseDTO<List> { Data = data, Success = true };
			}
			catch (Exception ex)
			{
				return new ResponseDTO<List> { Success = false, ErrorMessage = ex.Message };
			}
		}

		public async Task<ResponseDTO<dynamic>> GetListItems(GetSharePointModel sharepointModel)
		{
			try
			{
				var requestBuilderGetRequestConfiguration = new ItemsRequestBuilder.ItemsRequestBuilderGetQueryParameters();

				int i = 1;
				string filterString = string.Empty;
				foreach (var sharePointFiterModel in sharepointModel.SharePointFilterModels)
				{
					filterString += i != 1 ? " and " : "";
					filterString += "fields/" + sharePointFiterModel.Key + " " + sharePointFiterModel.Type + " " + "'" + sharePointFiterModel.Value + "'";
					i++;
				}
				if (!string.IsNullOrEmpty(filterString))
				{
					requestBuilderGetRequestConfiguration.Filter = filterString;
				}

				string fields = string.Empty;

				sharepointModel.Fields.ForEach(f =>
				{
					fields += f + ",";
				});

				if (!string.IsNullOrEmpty(fields))
				{
					fields = $"fields($select={fields})";
				}
				else
				{
					fields = "fields";
				}

				requestBuilderGetRequestConfiguration.Expand = [fields];

				
				var data = await _mgDAL.GetListItems(sharepointModel.SiteId, sharepointModel.ListId, sharepointModel.RecordCount, requestBuilderGetRequestConfiguration);
				List<dynamic> ts = new List<dynamic>();

				if (data != null)
				{
					foreach (var sharepoint in data)
					{
						ts.Add(new { id = sharepoint.Id, ParentId = sharepoint.ParentReference.Id, webUrl = sharepoint.WebUrl, contentType = sharepoint.ContentType.Name, sharePointListData = sharepoint.Fields.AdditionalData });
					}
				}

				return new ResponseDTO<dynamic> { Data = ts, Success = true };
			}
			catch (Exception ex)
			{
				return new ResponseDTO<dynamic> { Success = false, ErrorMessage = ex.Message };
			}
		}

		public async Task<ResponseDTO<byte[]>> DownloadFile(string siteId, string listId, string itemId)
		{
			try
			{
				var response = await _mgDAL.DownloadFile(siteId, listId, itemId);

				if (response != null)
				{
					using (MemoryStream ms = new MemoryStream())
					{
						response.CopyTo(ms);
						return new ResponseDTO<byte[]> { Data = ms.ToArray(), Success = true };
					}
				}
				else
					return new ResponseDTO<byte[]> { Success = false, ErrorMessage = "Unable to download file" };

			}
			catch (Exception ex)
			{
				return new ResponseDTO<byte[]> { Success = false, ErrorMessage = ex.Message };
			}
		}

		public async Task<ResponseDTO<List<string>>> AddListItems(AddSharePointModel sharePointModel)
		{
			try
			{
				var data = await _mgDAL.AddListItems(sharePointModel.SiteId, sharePointModel.ListId, sharePointModel.Items);
				return new ResponseDTO<List<string>> { Data = data, Success = true };
			}
			catch (Exception ex)
			{
				return new ResponseDTO<List<string>> { Success = false, ErrorMessage = ex.Message };
			}
		}

		public async Task<ResponseDTO<List<string>>> UpdateListItems(AddSharePointModel sharePointModel)
		{
			try
			{
				var data = await _mgDAL.UpdateListItems(sharePointModel.SiteId, sharePointModel.ListId, sharePointModel.Items);
				return new ResponseDTO<List<string>> { Data = data, Success = true };
			}
			catch (Exception ex)
			{
				return new ResponseDTO<List<string>> { Success = false, ErrorMessage = ex.Message };
			}
		}

		public async Task<ResponseDTO<bool>> DeleteListItems(GetSharePointModel sharepointModel)
		{
			try
			{
				int i = 1;
				string filterString = string.Empty;

				foreach (var sharePointFiterModel in sharepointModel.SharePointFilterModels)
				{
					filterString += i != 1 ? " and " : "";
					filterString += "fields/" + sharePointFiterModel.Key + " " + sharePointFiterModel.Type + " " + "'" + sharePointFiterModel.Value + "'";
					i++;
				}

				var options = new ItemsRequestBuilder.ItemsRequestBuilderGetQueryParameters()
				{
					Select = new string[] { "id" },
					Filter = filterString
				};


				await _mgDAL.DeleteListItems(sharepointModel.SiteId, sharepointModel.ListId, sharepointModel.RecordCount, options);
				return new ResponseDTO<bool> { Data = true, Success = true };
			}
			catch (Exception ex)
			{
				return new ResponseDTO<bool> { Success = false, ErrorMessage = ex.Message };
			}
		}

		public async Task<ResponseDTO<dynamic>> SearchListItems(SearchSharePointModel searchModel)
		{

			try
			{
				string searchString = string.Empty;

				if (!string.IsNullOrEmpty(searchModel.searchModels.SearchString))
				{
					searchString += $"\"{searchModel.searchModels.SearchString}\"";

				}

				if (!string.IsNullOrEmpty(searchModel.searchModels.SearchPath))
				{
					searchString += $" path:\"{searchModel.searchModels.SearchPath}\"";
				}

				searchString += " isDocument:true";

				List<string> selectFields = new List<string>();

				searchModel.searchModels.Fields.ForEach(f =>
				{
					selectFields.Add(f.ToString());
				});

				var requests = new List<SearchRequest>
				{
					new() {
						EntityTypes =
						[
							EntityType.ListItem
						],
						Query = new SearchQuery
						{
							QueryString = searchString
						},
						Fields = selectFields,
						From = searchModel.searchModels.From,
						Size = searchModel.searchModels.Size,
						Region = "US"
					}
				};

				var response = await _mgDAL.SearchListItems(requests);

				if (response == null)
				{
					return new ResponseDTO<dynamic> { Success = false, ErrorMessage = "Error querying from Sharepoint" };
				}

				using (JsonDocument doc = JsonDocument.Parse(response))
				{
					var root = doc.RootElement;
					var hitcontainers = root.GetProperty("value")[0].GetProperty("hitsContainers")[0];

					if (hitcontainers.GetProperty("total").GetInt32() != 0)
					{
						var hits = hitcontainers.GetProperty("hits").EnumerateArray();

						List<dynamic> searchResults = new List<dynamic>();


						foreach (var hit in hits)
						{
							var hitData = FlattenData(hit);
							searchResults.Add(hitData);
						}

						return new ResponseDTO<dynamic> { Success = true, Data = new { totalResults = hitcontainers.GetProperty("total").GetInt32(), searchResults } };
					}
				}

				return new ResponseDTO<dynamic> { Success = true, Data = Enumerable.Empty<int>().ToArray() };
			}
			catch (Exception e)
			{
				return new ResponseDTO<dynamic> { Success = false, ErrorMessage = e.Message };
			}
		}

		private static dynamic FlattenData(JsonElement data)
		{
			var searchData = new Dictionary<string, object>();

			foreach (var property in data.EnumerateObject())
			{
				var propertyName = property.Name;
				var propertyValue = property.Value;

				switch (propertyValue.ValueKind)
				{
					case JsonValueKind.Undefined:
						break;
					case JsonValueKind.Object:
						var objectData = FlattenData(propertyValue);

						searchData.Add(propertyName, objectData);

						break;

					case JsonValueKind.Array:
						var arrayData = new List<dynamic>();

						foreach (var arrayItem in propertyValue.EnumerateArray())
						{
							arrayData.Add(FlattenData(arrayItem));
						}

						searchData.Add(propertyName, arrayData);

						break;

					case JsonValueKind.String:
						searchData.Add(propertyName, propertyValue.GetString());

						break;

					case JsonValueKind.Number:
						searchData.Add(propertyName, propertyValue.GetInt32());

						break;

					case JsonValueKind.True:
						break;
					case JsonValueKind.False:
						break;
					case JsonValueKind.Null:
						break;
					default:
						break;
				}
			}

			return searchData;
		}
	}
}
