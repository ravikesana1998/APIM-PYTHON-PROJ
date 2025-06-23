var builder = Microsoft.AspNetCore.Builder.WebApplication.CreateBuilder(args);


// Add services to the container.
builder.Services.AddControllers()
				.AddJsonOptions(options =>
				{
					options.JsonSerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
				});
// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
builder.Services.AddApplicationInsightsTelemetry();
builder.Services.Configure<Config>(builder.Configuration.GetSection("MG"));

//builder.Services.AddAuthentication(NegotiateDefaults.AuthenticationScheme)
//				.AddNegotiate();

//builder.Services.AddAuthorization(options =>
//{
//	// By default, all incoming requests will be authorized according to the default policy.
//	options.FallbackPolicy = options.DefaultPolicy;
//});
builder.Services.AddScoped<IMessage_BLL, Message_BLL>();
builder.Services.AddScoped<ISharePoint_BLL, SharePoint_BLL>();
builder.Services.AddScoped<ITeams_BLL, Teams_BLL>();
builder.Services.AddScoped<IUsers_BLL, Users_BLL>();
builder.Services.AddScoped<IMG_DAL, MG_DAL>();
builder.Services.AddHealthChecks();
var app = builder.Build();

// Configure the HTTP request pipeline.
//if (!app.Environment.IsProduction())
//{
	app.UseSwagger();
	app.UseSwaggerUI();
	app.MapGet("/", context => Task.Run(() => context.Response.Redirect("swagger/index.html", true)));
//}

app.MapHealthChecks("/health", new Microsoft.AspNetCore.Diagnostics.HealthChecks.HealthCheckOptions
{
	ResultStatusCodes =
	{
		[HealthStatus.Healthy] = StatusCodes.Status200OK,
		[HealthStatus.Degraded] = StatusCodes.Status200OK,
		[HealthStatus.Unhealthy] = StatusCodes.Status503ServiceUnavailable
	}

});

app.UseHttpsRedirection();

//app.UseAuthentication();
//app.UseAuthorization();

app.MapControllers();

app.Run();
