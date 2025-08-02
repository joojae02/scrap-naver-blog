from naver_blog_api_wrapper import NaverBlogAPIWrapper

BLOG_CATEGORY_MAP = {
    "조양마트": {
        "blog_id": "joyangmart",
        "category": "와인입고소식",
    },
    "삐에로마켓": {
        "blog_id": "pierrot_market",
        "category": "와인소개",
    }
}


def main():
    blog_name = "" # 조양마트, 삐에로마켓

    blog_id = BLOG_CATEGORY_MAP[blog_name]["blog_id"]
    category_name = BLOG_CATEGORY_MAP[blog_name]["category"]

    naver_blog = NaverBlogAPIWrapper(blog_id)

    print(naver_blog.category_names())
    current_page_post_ids = naver_blog.get_post_ids(category_name)

    # TODO: DB 연결 후 기존 Scrap한 Post 제외
    # already_scraped_post_ids = ["1000000000000000000"]
    # new_post_ids = set(current_page_post_ids) - set(already_scraped_post_ids)

    # Default: Scrap Latest Post
    new_post_id = current_page_post_ids[-1] if current_page_post_ids else None
    
    print(new_post_id)

    result = naver_blog.get_contents(new_post_id)

    posted_images = []
    for image in result["images"]:
        if image.startswith("https://postfiles.pstatic.net"): # 실제 유저가 등록한 이미지
            # Replace any type parameter with w966 image size
            if "?type=" in image:
                image = image.split("?type=")[0] + "?type=w966"
            else:
                image = image + "?type=w966"
            posted_images.append(image)
    
    print("Content:", result["content"])
    print("Images:", posted_images)


if __name__ == "__main__":
    main()
