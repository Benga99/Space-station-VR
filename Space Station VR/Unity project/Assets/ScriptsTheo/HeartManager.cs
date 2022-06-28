using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class HeartManager : MonoBehaviour
{
    public List<GameObject> hearts;

    // Start is called before the first frame update
    void Start()
    {
        
        foreach (var h in hearts)
        {
            h.SetActive(false);
        }
        StartCoroutine(showHeart());
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    IEnumerator showHeart()
    {
        foreach(var h in hearts)
        {
            h.SetActive(true);
            h.GetComponent<SpriteRenderer>().material.color = new Color(h.GetComponent<SpriteRenderer>().material.color.r,
                                                                        h.GetComponent<SpriteRenderer>().material.color.g,
                                                                        h.GetComponent<SpriteRenderer>().material.color.b,
                                                                        0);
            StartCoroutine(createAndDeleteHeart(h));
            yield return new WaitForSeconds(0.5f);
        }
    }

    IEnumerator createAndDeleteHeart(GameObject h)
    {
        var matt = h.GetComponent<SpriteRenderer>().material;
        while (matt.color.a < 0.31f)
        {
            matt.color = new Color(matt.color.r, matt.color.g, matt.color.b, matt.color.a + 0.001f);
            yield return new WaitForEndOfFrame();
        }
        yield return new WaitForSeconds(5);
        //h.SetActive(false);
        matt = h.GetComponent<SpriteRenderer>().material;
        while(matt.color.a > 0)
        {
            matt.color = new Color(matt.color.r, matt.color.g, matt.color.b, matt.color.a - 0.001f);
            yield return new WaitForEndOfFrame();
        }
        h.SetActive(false);
    }
}
