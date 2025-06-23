namespace MG.BLL
{
	public interface ITeams_BLL
	{
		Task<ResponseDTO<List<Group>>> GetAllTeams(string searchString);
		Task<ResponseDTO<Group>> GetTeambyId(string id);
		Task<ResponseDTO<Group>> GetTeambyName(string id);
		Task<ResponseDTO<List<Channel>>> GetTeamChannels(string id);
		Task SendMessagetoUser(string userEmail, string body);
	}
}
