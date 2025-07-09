using System.Reflection;
using System.Text.Json.Serialization;
using Microsoft.AspNetCore.Diagnostics.HealthChecks;
using Microsoft.Extensions.Diagnostics.HealthChecks;

var builder = Microsoft.AspNetCore.Builder.WebApplication.CreateBuilder(args);

// ADD THIS BLOCK TO SUPPORT AZURE PORT BINDING
var port = Environment.GetEnvironmentVariable("PORT") ?? "80";
builder.WebHost.UseUrls($"http://*:{port}");

// Add services to the container.
builder.Services.AddControllers()
                .AddJsonOptions(options =>
                {
                    options.JsonSerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
                });

// Swagger/OpenAPI configuration
builder.Services.AddEndpointsApiExplorer();

builder.Services.AddSwaggerGen(options =>
{
    var xmlFilename = $"{Assembly.GetExecutingAssembly().GetName().Name}.xml";
    options.IncludeXmlComments(Path.Combine(AppContext.BaseDirectory, xmlFilename));
});

// Application Insights and Configuration
builder.Services.AddApplicationInsightsTelemetry();
builder.Services.Configure<Config>(builder.Configuration.GetSection("MG"));

// Dependency Injection
builder.Services.AddScoped<IMessage_BLL, Message_BLL>();
builder.Services.AddScoped<ISharePoint_BLL, SharePoint_BLL>();
builder.Services.AddScoped<ITeams_BLL, Teams_BLL>();
builder.Services.AddScoped<IUsers_BLL, Users_BLL>();
builder.Services.AddScoped<IMG_DAL, MG_DAL>();

// Health Checks
builder.Services.AddHealthChecks();

var app = builder.Build();

// Enable Swagger and redirect root to Swagger UI
app.UseSwagger();
app.UseSwaggerUI();
app.MapGet("/", context => Task.Run(() => context.Response.Redirect("swagger/index.html", true)));

app.MapHealthChecks("/health", new HealthCheckOptions
{
    ResultStatusCodes =
    {
        [HealthStatus.Healthy] = StatusCodes.Status200OK,
        [HealthStatus.Degraded] = StatusCodes.Status200OK,
        [HealthStatus.Unhealthy] = StatusCodes.Status503ServiceUnavailable
    }
});

app.UseHttpsRedirection();

// app.UseAuthentication();
// app.UseAuthorization();

app.MapControllers();

app.Run();
