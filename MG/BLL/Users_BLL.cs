namespace MG.BLL
{
	public class Users_BLL : IUsers_BLL
	{
		IMG_DAL _mgDAL;
		public Users_BLL(IMG_DAL mgDAL)
		{
			_mgDAL = mgDAL;
		}

		public async Task<ResponseDTO<User>> GetUserbyEmail(string email)
		{
			try
			{
				var user = await _mgDAL.GetUserbyEmail(email);
				return new ResponseDTO<User> { Data = user, Success = true };
			}
			catch (Exception ex)
			{
				return new ResponseDTO<User> { Success = false, ErrorMessage = ex.Message };
			}

		}
		//public static byte[] imageToByteArray(Image image)
		//{
		//	//image.AdditionalData.
		//	//using (var ms = new MemoryStream())
		//	//{
		//	//	image.(ms, image.AdditionalData);
		//	//	return ms.ToArray();
		//	//}
		//}
		public async Task<ResponseDTO<byte[]>> GetProfilePicturebyEmail(string email)
		{
			try
			{
				var user = await _mgDAL.GetProfilePicturebyEmail(email);
				return new ResponseDTO<byte[]> { Data = user, Success = true };
			}
			catch (Exception ex)
			{
				return new ResponseDTO<byte[]> { Success = false, ErrorMessage = ex.Message };
			}

		}
		public async Task<ResponseDTO<User>> GetUsersManagerbyEmail(string email)
		{
			try
			{
				var user = await _mgDAL.GetUsersManagerbyEmail(email);
				return new ResponseDTO<User> { Data = user, Success = true };
			}
			catch (Exception ex)
			{
				return new ResponseDTO<User> { Success = false, ErrorMessage = ex.Message };
			}
		}

		public async Task<ResponseDTO<dynamic>> CreateCalendarEvent(CalendarEventViewModel calendar)
		{
			try
			{
				var response = await _mgDAL.CreateCalendarEvent(calendar);
				return new ResponseDTO<dynamic> { Data = response, Success = true };
			}
			catch (Exception ex)
			{
				return new ResponseDTO<dynamic> { Success = false, ErrorMessage = ex.Message };
			}
		}

		//public async Task<ResponseDTO<string>> UpdateUsersManagerbyEmail(string userEmail, string managerEmail)
		//{
		//	var user = await GetUserbyEmail(userEmail);
		//	var manager = await GetUserbyEmail(managerEmail);
		//	if (user.Success && manager.Success)
		//	{
		//		try
		//		{
		//			await _mgDAL.UpdateUserManager(user.Data, manager.Data);
		//			return new ResponseDTO<string> { Data = "Manager updated successfully", Success = true };
		//		}
		//		catch (Exception ex)
		//		{
		//			return new ResponseDTO<string> { Success = false, ErrorMessage = ex.Message };
		//		}
		//	}

		//	return new ResponseDTO<string> { Success = false, ErrorMessage = "User/Manager not found" };
		//}
	}
}
