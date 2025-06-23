# Use official .NET SDK image to build and publish the app
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /app

# Copy .csproj and restore dependencies
COPY *.sln .
COPY MG/*.csproj ./MG/
RUN dotnet restore

# Copy everything else and build
COPY . ./
WORKDIR /app/MG
RUN dotnet publish -c Release -o /out

# Final image
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /out ./
ENTRYPOINT ["dotnet", "MG.dll"]
