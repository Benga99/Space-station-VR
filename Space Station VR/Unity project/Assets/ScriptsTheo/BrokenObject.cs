using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BrokenObject : MonoBehaviour
{
    public GameObject brokenObj;

    //float time = 0;
    bool broken = false;
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void OnCollisionEnter(Collision collision)
    {
        if (collision.gameObject.name == "Floorready" || collision.gameObject.tag == "Wall")
        {
            if (!broken)
            {
                StartCoroutine(breakable());
                broken = true;
            }

        }
       
    }

    private IEnumerator breakable()
    {
        //time = 0;
        brokenObj.SetActive(true);
        /*
        while (time < 0.2f)
        {
            yield return new WaitForEndOfFrame();
            time += Time.deltaTime;
        }
        */
        brokenObj.transform.position = transform.position;
        brokenObj.transform.rotation = transform.rotation;
        
        Destroy(gameObject);
        yield return new WaitForEndOfFrame();
    }
}
