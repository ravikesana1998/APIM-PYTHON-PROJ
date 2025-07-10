namespace MG.Controllers
{
	public class UsersController : BaseController
	{
		IUsers_BLL _usersBLL;
		public UsersController(IUsers_BLL usersBLL)
		{
			_usersBLL = usersBLL;
		}

		[HttpGet]
		public async Task<ActionResult> GetUserbyEmail(string email)
		{
			var response = await _usersBLL.GetUserbyEmail(email);
			return Ok(response);
		}

		[HttpGet]
		public async Task<ActionResult<ResponseDTO<byte[]>>> GetProfilePicturebyEmail(string email)
		{
			try
			{
				var response = await _usersBLL.GetProfilePicturebyEmail(email);
				return Ok(response);
			}
			catch (Exception ex)
			{
				return BadRequest(ex.Message);
			}
		}
		[HttpGet]
		public async Task<ActionResult> GetUsersManagerbyEmail(string email)
		{
			var response = await _usersBLL.GetUsersManagerbyEmail(email);
			return Ok(response);
		}

		[HttpPost]
		public async Task<ActionResult> CreateCalendarEvent(CalendarEventViewModel Calendar)
		{
			await _usersBLL.CreateCalendarEvent(Calendar);
			return Ok();
		}

		[HttpPut("{userEmail}/manager/{managerEmail}")]
		public async Task<ActionResult> UpdateUsersManagerbyEmail(string userEmail, string managerEmail)
		{
			var response = await _usersBLL.UpdateUsersManagerbyEmail(userEmail, managerEmail);
			return Ok(response);
		}
	}
}
