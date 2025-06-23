namespace MG.BLL
{
	public class Teams_BLL : ITeams_BLL
	{
		IMG_DAL mgDAL;
		public Teams_BLL(IMG_DAL dal)
		{
			mgDAL = dal;
		}

		public async Task<ResponseDTO<List<Group>>> GetAllTeams(string searchString)
		{
			try
			{
				var response = await mgDAL.GetAllTeams(searchString);
				return new ResponseDTO<List<Group>> { Data = response, Success = true };
			}
			catch (Exception ex)
			{
				return new ResponseDTO<List<Group>> { Success = false, ErrorMessage = ex.Message };
			}
		}

		public async Task<ResponseDTO<Group>> GetTeambyId(string id)
		{
			try
			{
				var response = await mgDAL.GetTeambyId(id);
				return new ResponseDTO<Group> { Data = response, Success = true };
			}
			catch (Exception ex)
			{
				return new ResponseDTO<Group> { Success = false, ErrorMessage = ex.Message };
			}
		}

		public async Task<ResponseDTO<Group>> GetTeambyName(string displayName)
		{
			try
			{
				var response = await mgDAL.GetTeambyName(displayName);
				return new ResponseDTO<Group> { Data = response, Success = true };
			}
			catch (Exception ex)
			{
				return new ResponseDTO<Group> { Success = false, ErrorMessage = ex.Message };
			}
		}

		public async Task<ResponseDTO<List<Channel>>> GetTeamChannels(string id)
		{
			try
			{
				var response = await mgDAL.GetTeamChannels(id);
				return new ResponseDTO<List<Channel>> { Data = response, Success = true };
			}
			catch (Exception ex)
			{
				return new ResponseDTO<List<Channel>> { Success = false, ErrorMessage = ex.Message };
			}
		}

		public async Task SendMessagetoUser(string userEmail, string body)
		{
			await mgDAL.SendMessagetoUser(userEmail, body);
		}
	}
}
