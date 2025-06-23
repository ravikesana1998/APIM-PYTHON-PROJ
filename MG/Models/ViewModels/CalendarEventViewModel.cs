namespace MG.Models.ViewModels
{
	public class CalendarEventViewModel
	{
		public string MeetingLink { get; set; }
		public string dutyOfficerEmail { get; set; }
		public string dutyOfficerDisplayName { get; set; }
		public string startDatetime { get; set; }
		public string attendeeEmail { get; set; }
		public string attendeeDisplayName { get; set; }
		public string timeZone { get; set; }
	}
}
