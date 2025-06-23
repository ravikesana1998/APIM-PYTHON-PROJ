namespace MG.Controllers
{
	public class TeamsController : BaseController
	{
		ITeams_BLL teamsBLL;
		public TeamsController(ITeams_BLL bll)
		{
			teamsBLL = bll;
		}

		[HttpGet("{searchString}")]
		public async Task<ActionResult> GetAllTeams(string searchString)
		{
			var response = await teamsBLL.GetAllTeams(searchString);
			return Ok(response);
		}

		[HttpGet("{id}")]
		public async Task<ActionResult> GetTeambyId(string id)
		{
			var response = await teamsBLL.GetTeambyId(id);
			return Ok(response);
		}

		[HttpGet("{displayName}")]
		public async Task<ActionResult> GetTeambyName(string displayName)
		{
			var response = await teamsBLL.GetTeambyName(displayName);
			return Ok(response);
		}

		[HttpGet("{id}")]
		public async Task<ActionResult> GetTeamChannels(string id)
		{
			var response = await teamsBLL.GetTeamChannels(id);
			return Ok(response);
		}

		[HttpPost("{userEmail}")]
		public void SendMessagetoUser(string userEmail, [FromBody] string body)
		{
			teamsBLL.SendMessagetoUser(userEmail, body);
		}
	}
}
