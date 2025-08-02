import json
import re
from typing import List
import requests
from bs4 import BeautifulSoup

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


class NaverBlog:
    def __init__(self, naver_blog_id: str) -> None:
        self.naver_blog_id = naver_blog_id
        self._get_categories()

    def _get_categories(self):
        response = requests.get(
            f"https://m.blog.naver.com/rego/CategoryList.nhn?blogId={self.naver_blog_id}",
            headers={"Referer": f"https://m.blog.naver.com"},
        )
        
        data = json.loads(response.text.split("\n")[1])["result"]["mylogCategoryList"]
        self.categories = {
            d["categoryName"].replace("\xa0", "").replace(" ", ""): (d["categoryNo"], d["parentCategoryNo"])
            for d in data
            if not d["divisionLine"]
        }
        self.categories["전체글"] = (0, None)

    def category_names(self):
        return list(self.categories.keys())

    def get_post_ids(self, category_name) -> List[str]:
        url = "http://blog.naver.com/PostTitleListAsync.nhn"
        post_ids = set()

        params = {
            "blogId": self.naver_blog_id,
            "currentPage": 1,
            "categoryNo": self.categories[category_name][0],
            "parentCategoryNo": self.categories[category_name][1],
            "countPerPage": 5,
            "viewdate": "",
        }


        try:
            response = requests.get(url, params=params)
            data = json.loads(response.text.replace("\\", "\\\\"))
            lists = data["postList"]
        except Exception as e:
            print(f"API Error occured restart... {e}")
            return []

        ids = [d["logNo"] for d in lists]

        if ids[0] not in post_ids:
            post_ids.update(ids)
            params["currentPage"] += 1
        else:
            print(f"Get post ids: {len(post_ids)} posts found.")
        return sorted(list(post_ids))

    def get_contents(self, post_id: str) -> dict:
        url = f"http://blog.naver.com/PostView.nhn"
        params = {"blogId": self.naver_blog_id}

        params["logNo"] = post_id

        response = requests.get(url, params=params)

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.select_one(f"#post-view{post_id} > div > div.se-main-container")

        if not text:
            print(f"[Error] cannot select content in {post_id}.")
            return {}
        
        content = ""
        content = text.get_text("\n").replace("\xa0", " ")  # Space unicode replace
        content = re.sub(r"\s+", " ", content).strip()

        images = []
        img_tags = text.find_all('img')
        images = [img.get('src') for img in img_tags]

        return {
            "content": content,
            "images": images
        }

def main():
    blog_name = "" # 조양마트, 삐에로마켓

    blog_id = BLOG_CATEGORY_MAP[blog_name]["blog_id"]
    category_name = BLOG_CATEGORY_MAP[blog_name]["category"]

    naver_blog = NaverBlog(blog_id)

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
