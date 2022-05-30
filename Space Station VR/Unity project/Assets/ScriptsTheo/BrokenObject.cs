using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BrokenObject : MonoBehaviour
{
    public GameObject brokenObj;

    float time = 0;
    bool broken = false;
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        Debug.Log(time);
        time += Time.deltaTime;

        if(time > 4.8f)
        {
            brokenObj.SetActive(true);
        }
        if (time > 5 && !broken)
        {
            
            brokenObj.transform.position = transform.position;
            brokenObj.transform.rotation = transform.rotation;
            

            Destroy(gameObject);

            broken = true;
        }
    }
}
