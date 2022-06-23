using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Valve.VR;
using Valve.VR.InteractionSystem;

public class ChessGame : MonoBehaviour
{
    public GameObject image;
    List<GameObject> pieces = new List<GameObject>();

    public GameObject LeoSign;
    public GameObject SodaSign;

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
        if(other.gameObject.CompareTag("Chess") && !pieces.Contains(other.gameObject))
        {
            pieces.Add(other.gameObject);
        }
        if(pieces.Count == 4)
        {
            StartCoroutine(showImage());
            pieces.Add(other.gameObject);
        }
    }

    private IEnumerator showImage()
    {
        float pos = 0f;
        while(pos < 0.16f)
        {
            image.transform.position = new Vector3(image.transform.position.x + Time.deltaTime / 10f, image.transform.position.y, image.transform.position.z);
            pos += Time.deltaTime / 10f;
            yield return new WaitForEndOfFrame();
        }
        LeoSign.SetActive(true);
        SodaSign.SetActive(true);
        image.GetComponent<Interactable>().enabled = true;
        //write on the soda
    }
}
