using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DoorFuntionality : MonoBehaviour
{
    public GameObject cat;
    public GameObject bat;

    public bool fridgeOpened = false;
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void OnTriggerEnter(Collider other)
    {
        if (!fridgeOpened)
        {
            StartCoroutine(OpenDoor());
            fridgeOpened = true;
            cat.SetActive(true);
            bat.SetActive(true);
        }
    }

    private IEnumerator OpenDoor()
    {
        float rot = 0f;
        while(rot < 45f)
        {
            rot += Time.fixedDeltaTime * 10f;
            this.gameObject.transform.parent.gameObject.transform.Rotate(0, -Time.fixedDeltaTime * 10f, 0);
            yield return new WaitForFixedUpdate();
        }
        //TODO: Sa fac un obiect care iese din frigider cand este deschis
    }
}
