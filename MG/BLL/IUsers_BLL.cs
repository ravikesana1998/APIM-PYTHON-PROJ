namespace MG.BLL
{
	public interface IUsers_BLL
	{
		Task<ResponseDTO<User>> GetUserbyEmail(string email);
		Task<ResponseDTO<User>> GetUsersManagerbyEmail(string email);
		Task<ResponseDTO<byte[]>> GetProfilePicturebyEmail(string email);
		Task<ResponseDTO<dynamic>> CreateCalendarEvent(CalendarEventViewModel calendar);

		//Task<ResponseDTO<string>> UpdateUsersManagerbyEmail(string userEmail, string managerEmail);
	}
}
