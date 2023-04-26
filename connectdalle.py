import openai



def imagegenai(prompt):
    my_api = "YOUR TOKEN"
    openai.api_key = my_api

    response = openai.Image.create(
        prompt=prompt,
        size="1024x1024",
        response_format="url"
    )

    return response["data"][0]["url"]



