from supabase import create_client, Client


SUPABASE_URL = "https://bbrvvbipmfdiyekyilbo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJicnZ2YmlwbWZkaXlla3lpbGJvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIwMzc5MzMsImV4cCI6MjA2NzYxMzkzM30.FBzWwcIrorGSHg49CV-nmEyNxZHnewwwL5QMu3Gofrs"

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Please set SUPABASE_URL and SUPABASE_KEY.")

# Initialize Supabase client
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Fetch all media clips from the database
def fetch_media_clips():
    supabase = get_supabase_client()
    # queries the media_clips table and selects all columns 
    response = supabase.table('media_clips').select('*').execute()
    #print(response)
    
    return response.data

if __name__ == "__main__":
    clips = fetch_media_clips()
    for clip in clips:
        print(clip) 