namespace MG.Models
{
	public class ResponseDTO<T>
	{
		public bool Success { get; set; }
		public string ErrorMessage { get; set; }
		public T Data { get; set; }
	}
}
